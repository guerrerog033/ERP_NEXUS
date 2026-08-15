from __future__ import annotations

from pathlib import Path

from aplicacion.integraciones.dian.cliente_emision import (
    ClienteEmisionDian,
)
from aplicacion.integraciones.dian.firmador_xml import (
    FirmadorXml,
)
from aplicacion.integraciones.dian.generador_nomina_electronica import (
    GeneradorNominaElectronica,
)
from aplicacion.modulos.contabilidad.servicios import (
    ServicioContabilidad,
)
from aplicacion.modulos.nomina.exportadores.pila import (
    ExportadorPila,
)
from aplicacion.modulos.nomina.repositorio import (
    RepositorioPeriodoNomina,
)
from aplicacion.modulos.nomina.servicios import (
    ServicioNomina,
)
from aplicacion.nucleo.configuracion import Configuracion


class IntegracionNomina:

    @classmethod
    def contabilizar(
        cls,
        periodo_id: int,
    ):

        periodo = ServicioNomina.obtener_periodo(
            periodo_id,
        )

        if periodo is None:

            raise ValueError(
                "Periodo no encontrado.",
            )

        if periodo.estado != "liquidado":

            raise ValueError(
                "Debe liquidar el periodo antes de contabilizar.",
            )

        if periodo.contabilizado:

            raise ValueError(
                "El periodo ya fue contabilizado.",
            )

        totales = ServicioNomina.totales_periodo(
            periodo_id,
        )

        if totales["neto"] <= 0:

            raise ValueError(
                "No hay valores de nómina para contabilizar.",
            )

        asiento = ServicioContabilidad.registrar_liquidacion_nomina(
            periodo,
            totales,
        )

        return RepositorioPeriodoNomina.actualizar_integracion(
            periodo_id,
            contabilizado=True,
            asiento_id=asiento.id,
        )

    @classmethod
    def exportar_pila(
        cls,
        periodo_id: int,
    ) -> dict[str, str]:

        periodo = ServicioNomina.obtener_periodo(
            periodo_id,
        )

        if periodo is None:

            raise ValueError(
                "Periodo no encontrado.",
            )

        if periodo.estado != "liquidado":

            raise ValueError(
                "Debe liquidar el periodo antes de exportar PILA.",
            )

        filas = ServicioNomina.datos_pila_periodo(
            periodo_id,
        )

        if not filas:

            raise ValueError(
                "No hay liquidaciones para exportar.",
            )

        modo = str(
            Configuracion.obtener(
                "nomina",
                "formato_pila",
            )
            or "aportes_en_linea",
        ).lower()

        if modo == "simplificado":

            ruta = ExportadorPila.generar(
                anio=periodo.anio,
                mes=periodo.mes,
                liquidaciones=filas,
            )

            rutas = {
                "tipo2": ruta,
                "tipo1": "",
            }

        else:

            rutas = ExportadorPila.generar_aportes_en_linea(
                anio=periodo.anio,
                mes=periodo.mes,
                aportante=ServicioNomina.datos_aportante(),
                liquidaciones=filas,
            )

        RepositorioPeriodoNomina.actualizar_integracion(
            periodo_id,
            ruta_pila=rutas.get(
                "tipo2",
                "",
            ),
        )

        return rutas

    @classmethod
    def emitir_electronica(
        cls,
        periodo_id: int,
    ) -> dict:

        periodo = ServicioNomina.obtener_periodo(
            periodo_id,
        )

        if periodo is None:

            raise ValueError(
                "Periodo no encontrado.",
            )

        if periodo.estado != "liquidado":

            raise ValueError(
                "Debe liquidar el periodo antes de emitir nómina electrónica.",
            )

        if periodo.estado_dian in (
            "aceptada",
            "enviada",
        ):

            raise ValueError(
                "La nómina electrónica ya fue enviada.",
            )

        totales = ServicioNomina.totales_periodo(
            periodo_id,
        )

        trabajadores = ServicioNomina.datos_trabajadores_dian(
            periodo_id,
        )

        numero = (
            f"NE{periodo.anio:04d}"
            f"{periodo.mes:02d}"
        )

        emision = GeneradorNominaElectronica.generar(
            numero=numero,
            anio=periodo.anio,
            mes=periodo.mes,
            valor_total=totales["neto"],
            trabajadores=trabajadores,
        )

        xml_final = emision.xml
        mensaje_firma = ""

        try:

            xml_final = FirmadorXml.firmar(
                emision.xml,
                ruta_salida=emision.ruta_xml,
            )

        except ValueError as error:

            if Configuracion.obtener(
                "dian",
                "certificado_ruta",
            ):

                raise

            mensaje_firma = str(error)

        nombre_xml = Path(
            emision.ruta_xml,
        ).name

        from aplicacion.integraciones.dian.contenedor_electronico import (
            adjuntos_contenedor_nomina_electronica,
        )

        resultado = ClienteEmisionDian.enviar(
            nombre_xml=nombre_xml,
            xml_firmado=xml_final,
            adjuntos_contenedor=adjuntos_contenedor_nomina_electronica(
                periodo,
                nombre_xml=nombre_xml,
                cune=emision.cune,
                numero=emision.numero,
                totales=totales,
                trabajadores=trabajadores,
            ),
        )

        if resultado.exito:

            estado_dian = "aceptada"

        elif resultado.estado:

            estado_dian = resultado.estado

        else:

            estado_dian = "pendiente"

        if (
            not resultado.exito
            and not Configuracion.obtener(
                "dian",
                "certificado_ruta",
            )
        ):

            estado_dian = "sin_firma"

        mensaje = resultado.mensaje or mensaje_firma

        if resultado.error and not mensaje:

            mensaje = resultado.error

        RepositorioPeriodoNomina.actualizar_integracion(
            periodo_id,
            estado_dian=estado_dian,
            cune=emision.cune,
            ruta_xml=emision.ruta_xml,
            mensaje_dian=mensaje or "",
            ruta_zip=resultado.ruta_zip,
        )

        return {
            "cune": emision.cune,
            "ruta_xml": emision.ruta_xml,
            "estado_dian": estado_dian,
            "mensaje": mensaje,
            "ruta_zip": resultado.ruta_zip,
        }
