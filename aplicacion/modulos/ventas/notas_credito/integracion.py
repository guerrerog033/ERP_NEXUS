from __future__ import annotations

from aplicacion.modulos.contabilidad.servicios import (
    ServicioContabilidad,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioNotaCreditoVenta
from .servicios import ServicioNotaCreditoVenta


class IntegracionNotaCreditoVenta:

    @classmethod
    def _aplicar_efectos_operativos(
        cls,
        id_registro: int,
    ) -> None:

        nota = ServicioNotaCreditoVenta.obtener_completa(
            id_registro,
        )

        if (
            nota is None
            or nota.inventario_aplicado
        ):

            return

        RepositorioNotaCreditoVenta.reducir_saldo_factura(
            nota.factura_id,
            float(
                nota.total or 0,
            ),
        )

        from aplicacion.modulos.inventario.servicios import (
            ServicioInventario,
        )

        ServicioInventario.registrar_entrada_nota_credito_venta(
            nota,
        )

    @classmethod
    def confirmar_generacion(
        cls,
        id_registro: int,
        *,
        emitir_dian: bool = False,
    ):

        nota = ServicioNotaCreditoVenta.obtener_completa(
            id_registro,
        )

        if nota is None:

            raise ValueError(
                "No se encontró la nota crédito.",
            )

        if nota.estado == "borrador":

            RepositorioNotaCreditoVenta.actualizar_estado_confirmacion(
                id_registro,
                estado="generada",
            )

        elif nota.estado not in (
            "generada",
            "emitida",
            "contabilizada",
        ):

            raise ValueError(
                "La nota crédito no puede confirmarse "
                "en este estado.",
            )

        cls._aplicar_efectos_operativos(
            id_registro,
        )

        if emitir_dian:

            nota = ServicioNotaCreditoVenta.obtener_completa(
                id_registro,
            )

            if (
                nota is not None
                and nota.estado
                not in (
                    "emitida",
                )
            ):

                cls.emitir_electronica(
                    id_registro,
                )

        else:

            cls._contabilizar_si_configurado(
                id_registro,
            )

        return ServicioNotaCreditoVenta.obtener_completa(
            id_registro,
        )

    @classmethod
    def emitir_electronica(
        cls,
        id_registro: int,
    ):

        from pathlib import Path

        from aplicacion.integraciones.dian.cliente_emision import (
            ClienteEmisionDian,
        )
        from aplicacion.integraciones.dian.firmador_xml import (
            FirmadorXml,
        )
        from aplicacion.integraciones.dian.generador_nota_credito import (
            GeneradorNotaCreditoVenta,
        )

        nota = ServicioNotaCreditoVenta.obtener_completa(
            id_registro,
        )

        if nota is None:

            raise ValueError(
                "No se encontró la nota crédito.",
            )

        if nota.estado == "emitida":

            raise ValueError(
                "La nota crédito ya fue emitida.",
            )

        if nota.estado == "borrador":

            RepositorioNotaCreditoVenta.actualizar_estado_confirmacion(
                id_registro,
                estado="generada",
            )

        datos = GeneradorNotaCreditoVenta.generar(
            nota,
        )

        xml_final = datos.xml
        mensaje_firma = ""

        try:

            xml_final = FirmadorXml.firmar(
                datos.xml,
                ruta_salida=datos.ruta_xml,
            )

        except ValueError as error:

            if Configuracion.obtener(
                "dian",
                "certificado_ruta",
            ):

                raise

            mensaje_firma = str(error)

        nombre_xml = Path(
            datos.ruta_xml,
        ).name

        from aplicacion.integraciones.dian.contenedor_electronico import (
            adjuntos_contenedor_nota_credito,
        )

        resultado = ClienteEmisionDian.enviar(
            nombre_xml=nombre_xml,
            xml_firmado=xml_final,
            adjuntos_contenedor=adjuntos_contenedor_nota_credito(
                nota,
                nombre_xml=nombre_xml,
                cufe=datos.cufe,
            ),
        )

        estado = "emitida"

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

            estado = "generada"
            estado_dian = "sin_firma"

        mensaje = resultado.mensaje or mensaje_firma

        if resultado.error and not mensaje:

            mensaje = resultado.error

        RepositorioNotaCreditoVenta.actualizar_emision(
            id_registro,
            cufe=datos.cufe,
            estado=estado,
            estado_dian=estado_dian,
            mensaje_dian=mensaje or "",
            ruta_xml=datos.ruta_xml,
            ruta_zip=resultado.ruta_zip,
        )

        cls._aplicar_efectos_operativos(
            id_registro,
        )

        cls._contabilizar_si_configurado(
            id_registro,
        )

        return resultado

    @classmethod
    def contabilizar(
        cls,
        id_registro: int,
    ):

        nota = ServicioNotaCreditoVenta.obtener_completa(
            id_registro,
        )

        if nota is None:

            raise ValueError(
                "No se encontró la nota crédito.",
            )

        if nota.contabilizado:

            raise ValueError(
                "La nota crédito ya está contabilizada.",
            )

        if nota.estado in (
            "borrador",
        ):

            raise ValueError(
                "Emita o genere la nota crédito antes "
                "de contabilizar.",
            )

        asiento = ServicioContabilidad.registrar_nota_credito_venta(
            nota,
        )

        RepositorioNotaCreditoVenta.actualizar_contabilizacion(
            id_registro,
            asiento_id=asiento.id,
        )

        return asiento

    @classmethod
    def _contabilizar_si_configurado(
        cls,
        id_registro: int,
    ) -> None:

        if not Configuracion.obtener(
            "ventas",
            "contabilizar_automatico",
        ):

            return

        try:

            cls.contabilizar(
                id_registro,
            )

        except ValueError:

            pass
