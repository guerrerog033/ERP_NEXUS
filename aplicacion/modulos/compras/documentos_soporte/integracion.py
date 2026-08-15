from __future__ import annotations

from pathlib import Path

from aplicacion.integraciones.dian.cliente_emision import (
    ClienteEmisionDian,
)
from aplicacion.integraciones.dian.firmador_xml import (
    FirmadorXml,
)
from aplicacion.integraciones.dian.generador_documento_soporte import (
    GeneradorDocumentoSoporte,
)
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioDocumentoSoporte
from .servicios import ServicioDocumentoSoporte


class IntegracionDocumentoSoporte:

    @classmethod
    def emitir_electronica(
        cls,
        id_registro: int,
    ):

        documento = ServicioDocumentoSoporte.obtener_completa(
            id_registro,
        )

        if documento is None:

            raise ValueError(
                "No se encontró el documento soporte.",
            )

        if documento.estado == "emitido":

            raise ValueError(
                "El documento soporte ya fue emitido.",
            )

        datos = GeneradorDocumentoSoporte.generar(
            documento,
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
            adjuntos_contenedor_documento_soporte,
        )

        resultado = ClienteEmisionDian.enviar(
            nombre_xml=nombre_xml,
            xml_firmado=xml_final,
            adjuntos_contenedor=adjuntos_contenedor_documento_soporte(
                documento,
                nombre_xml=nombre_xml,
                cuds=datos.cuds,
            ),
        )

        estado = "emitido"

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

            estado = "generado"
            estado_dian = "sin_firma"

        mensaje = resultado.mensaje or mensaje_firma

        if resultado.error and not mensaje:

            mensaje = resultado.error

        RepositorioDocumentoSoporte.actualizar_emision(
            id_registro,
            cuds=datos.cuds,
            estado=estado,
            estado_dian=estado_dian,
            mensaje_dian=mensaje or "",
            ruta_xml=datos.ruta_xml,
        )

        return resultado
