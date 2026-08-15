from __future__ import annotations

from pathlib import Path

from aplicacion.integraciones.dian.cliente_emision import (
    ClienteEmisionDian,
)
from aplicacion.integraciones.dian.firmador_xml import (
    FirmadorXml,
)
from aplicacion.integraciones.dian.generador_guia_remision import (
    GeneradorGuiaRemision,
)
from aplicacion.maestros.terceros.servicio import (
    TerceroServicio,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioGuiaRemisionElectronica
from .servicios import ServicioGuiaRemisionElectronica


class IntegracionGuiaRemisionElectronica:

    @classmethod
    def emitir_electronica(
        cls,
        id_registro: int,
    ):

        guia = ServicioGuiaRemisionElectronica.obtener_completa(
            id_registro,
        )

        if guia is None:

            raise ValueError(
                "No se encontró la guía de remisión.",
            )

        if guia.estado == "emitida":

            raise ValueError(
                "La guía electrónica ya fue emitida.",
            )

        cliente = TerceroServicio.obtener_por_id(
            guia.cliente_id,
        )

        nit_cliente = ""
        razon_cliente = ""

        if cliente is not None:

            nit_cliente = (
                cliente.numero_documento
                or ""
            )

            razon_cliente = (
                cliente.razon_social
                or cliente.nombre_comercial
                or cliente.nombre_completo
                or ""
            )

        datos = GeneradorGuiaRemision.generar(
            guia,
            nit_cliente=nit_cliente,
            razon_cliente=razon_cliente,
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
            adjuntos_contenedor_guia_remision,
        )

        resultado = ClienteEmisionDian.enviar(
            nombre_xml=nombre_xml,
            xml_firmado=xml_final,
            adjuntos_contenedor=adjuntos_contenedor_guia_remision(
                guia,
                nombre_xml=nombre_xml,
                cude=datos.cude,
            ),
        )

        estado = "emitida"

        if resultado.exito:

            estado_dian = "aceptado"

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

        RepositorioGuiaRemisionElectronica.actualizar_emision(
            id_registro,
            cude=datos.cude,
            estado=estado,
            estado_dian=estado_dian,
            mensaje_dian=mensaje or "",
            ruta_xml=datos.ruta_xml,
        )

        return resultado
