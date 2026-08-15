from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aplicacion.integraciones.dian.cliente_recepcion import (
    ClienteRecepcionDian,
)
from aplicacion.integraciones.dian.firmador_xml import (
    FirmadorXml,
)
from aplicacion.integraciones.dian.generador_acuse_recibo import (
    CODIGO_ACUSE_RECIBO,
    EVENTOS_RADIAN,
    GeneradorAcuseRecibo,
)
from aplicacion.integraciones.dian.servicio_acuse_recibo import (
    ServicioAcuseRecibo,
)
from aplicacion.modulos.compras.facturas.repositorio import (
    RepositorioFacturaCompra,
)
from aplicacion.modulos.compras.facturas.repositorio_eventos_radian import (
    RepositorioFacturaCompraEventoRadian,
)
from aplicacion.modulos.compras.facturas.servicios import (
    ServicioFacturaCompra,
)


@dataclass(slots=True)
class ResultadoEventoRadian:

    exito: bool = False
    estado: str = ""
    mensaje: str = ""
    cude: str = ""
    codigo_evento: str = ""
    error: str = ""


class ServicioEventosRadian:
    """
    Genera y envía eventos RADIAN 030–049
    sobre facturas de compra recibidas.
    """

    EVENTOS_UI = (
        (
            "031",
            "Recibo bien/servicio",
        ),
        (
            "032",
            "Aceptación expresa",
        ),
        (
            "033",
            "Aceptación tácita",
        ),
        (
            "034",
            "Reclamo",
        ),
    )

    @classmethod
    def codigos_soportados(cls) -> tuple[str, ...]:

        return tuple(
            sorted(
                EVENTOS_RADIAN.keys(),
            ),
        )

    @classmethod
    def procesar(
        cls,
        id_registro: int,
        codigo_evento: str,
        *,
        forzar: bool = False,
    ) -> ResultadoEventoRadian:

        codigo = str(
            codigo_evento or CODIGO_ACUSE_RECIBO,
        ).zfill(3)[-3:]

        if codigo == CODIGO_ACUSE_RECIBO:

            resultado = ServicioAcuseRecibo.procesar(
                id_registro,
                forzar=forzar,
            )

            return ResultadoEventoRadian(
                exito=resultado.exito,
                estado=resultado.estado,
                mensaje=resultado.mensaje,
                cude=resultado.cude,
                codigo_evento=codigo,
                error=resultado.error,
            )

        factura = ServicioFacturaCompra.obtener_completa(
            id_registro,
        )

        if factura is None:

            return ResultadoEventoRadian(
                codigo_evento=codigo,
                error="No se encontró la factura.",
            )

        if not factura.cufe:

            return ResultadoEventoRadian(
                codigo_evento=codigo,
                error=(
                    "La factura no tiene CUFE para "
                    "generar el evento RADIAN."
                ),
            )

        if (
            RepositorioFacturaCompraEventoRadian.existe_exitoso(
                id_registro,
                codigo,
            )
            and not forzar
        ):

            return ResultadoEventoRadian(
                exito=True,
                estado="registrado",
                mensaje=(
                    factura.evento_radian_mensaje
                    or "Evento RADIAN ya registrado."
                ),
                cude=factura.evento_radian_cude or "",
                codigo_evento=codigo,
            )

        try:

            datos = GeneradorAcuseRecibo.generar(
                cufe_factura=factura.cufe or "",
                numero_factura=(
                    factura.numero_proveedor
                    or factura.numero
                ),
                fecha_factura=factura.fecha,
                nit_emisor=factura.nit_proveedor or "",
                razon_emisor=(
                    factura.razon_social_proveedor
                    or ""
                ),
                valor_total=float(
                    factura.total or 0,
                ),
                codigo_evento=codigo,
            )

            ruta_xml = GeneradorAcuseRecibo.guardar_xml(
                datos,
                cufe_factura=factura.cufe or "",
            )

            xml_firmado = datos.xml

            try:

                xml_firmado = FirmadorXml.firmar(
                    datos.xml,
                )

                Path(ruta_xml).write_text(
                    xml_firmado,
                    encoding="utf-8",
                )

            except ValueError:

                pass

            respuesta_api = (
                ClienteRecepcionDian.enviar_acuse_recibo(
                    cufe=factura.cufe or "",
                    numero_factura=(
                        factura.numero_proveedor
                        or factura.numero
                    ),
                    nit_proveedor=(
                        factura.nit_proveedor or ""
                    ),
                    xml_evento=xml_firmado,
                    codigo_evento=codigo,
                )
            )

            estado = (
                "aceptado"
                if respuesta_api.exito
                else "enviado"
            )

            mensaje = (
                respuesta_api.mensaje
                or GeneradorAcuseRecibo.descripcion_evento(
                    codigo,
                )
            )

            if respuesta_api.error:

                estado = "error"
                mensaje = respuesta_api.error

            RepositorioFacturaCompraEventoRadian.registrar(
                id_registro,
                codigo=codigo,
                cude=datos.cude,
                estado=estado,
                mensaje=mensaje,
                ruta_xml=ruta_xml,
                forzado=forzar,
            )

            return ResultadoEventoRadian(
                exito=estado
                in (
                    "enviado",
                    "aceptado",
                    "registrado",
                ),
                estado=estado,
                mensaje=mensaje,
                cude=datos.cude,
                codigo_evento=codigo,
                error=respuesta_api.error,
            )

        except Exception as error:

            RepositorioFacturaCompraEventoRadian.registrar(
                id_registro,
                codigo=codigo,
                estado="error",
                mensaje=str(error),
                forzado=forzar,
            )

            return ResultadoEventoRadian(
                estado="error",
                codigo_evento=codigo,
                error=str(error),
            )
