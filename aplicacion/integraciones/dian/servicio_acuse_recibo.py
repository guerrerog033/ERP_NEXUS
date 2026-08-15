from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from aplicacion.integraciones.dian.cliente_recepcion import (
    ClienteRecepcionDian,
)
from aplicacion.integraciones.dian.firmador_xml import (
    FirmadorXml,
)
from aplicacion.integraciones.dian.generador_acuse_recibo import (
    GeneradorAcuseRecibo,
)
from aplicacion.nucleo.configuracion import Configuracion

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
class ResultadoAcuseRecibo:

    exito: bool = False
    estado: str = ""
    mensaje: str = ""
    cude: str = ""
    error: str = ""


class ServicioAcuseRecibo:
    """
    Genera y envía el acuse de recibo RADIAN (030)
    para facturas de compra a crédito.
    """

    @classmethod
    def _config(cls) -> dict:

        compras = dict(
            Configuracion.obtener(
                "compras",
            )
            or {},
        )

        recepcion = dict(
            Configuracion.obtener(
                "dian",
                "recepcion_compras",
            )
            or {},
        )

        return {
            **recepcion,
            "auto_acuse_recibo_credito": compras.get(
                "auto_acuse_recibo_credito",
                recepcion.get(
                    "auto_acuse_recibo_credito",
                    True,
                ),
            ),
        }

    @classmethod
    def auto_habilitado(cls) -> bool:

        return bool(
            cls._config().get(
                "auto_acuse_recibo_credito",
                True,
            ),
        )

    @classmethod
    def campos_desde_xml(
        cls,
        parseada,
    ) -> dict:

        es_credito = bool(
            getattr(
                parseada,
                "es_credito",
                False,
            ),
        )

        return {
            "es_credito": es_credito,
            "requiere_acuse_recibo": es_credito,
            "acuse_recibo_estado": (
                "pendiente"
                if es_credito
                else "no_aplica"
            ),
            "estado_pago": (
                "credito"
                if es_credito
                else "pendiente"
            ),
        }

    @classmethod
    def procesar(
        cls,
        id_registro: int,
        *,
        forzar: bool = False,
    ) -> ResultadoAcuseRecibo:

        factura = ServicioFacturaCompra.obtener_completa(
            id_registro,
        )

        if factura is None:

            return ResultadoAcuseRecibo(
                error="No se encontró la factura.",
            )

        if not factura.requiere_acuse_recibo:

            return ResultadoAcuseRecibo(
                estado="no_aplica",
                mensaje="La factura no requiere acuse de recibo.",
            )

        if (
            factura.acuse_recibo_estado
            in (
                "enviado",
                "aceptado",
            )
            and not forzar
        ):

            return ResultadoAcuseRecibo(
                exito=True,
                estado=factura.acuse_recibo_estado,
                mensaje=(
                    factura.acuse_recibo_mensaje
                    or "Acuse de recibo ya registrado."
                ),
                cude=factura.acuse_recibo_cude or "",
            )

        if (
            not forzar
            and not cls.auto_habilitado()
        ):

            return ResultadoAcuseRecibo(
                estado="pendiente",
                mensaje=(
                    "Acuse pendiente. "
                    "Active auto_acuse_recibo_credito "
                    "o envíe manualmente."
                ),
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
                    codigo_evento="030",
                )
            )

            estado = (
                "aceptado"
                if respuesta_api.exito
                else "enviado"
            )

            mensaje = (
                respuesta_api.mensaje
                or "Acuse de recibo generado."
            )

            if respuesta_api.error:

                estado = "error"
                mensaje = respuesta_api.error

            RepositorioFacturaCompra.actualizar_acuse_recibo(
                id_registro,
                estado=estado,
                cude=datos.cude,
                mensaje=mensaje,
                ruta_xml=ruta_xml,
            )

            RepositorioFacturaCompraEventoRadian.registrar(
                id_registro,
                codigo="030",
                cude=datos.cude,
                estado=estado,
                mensaje=mensaje,
                ruta_xml=ruta_xml,
                forzado=forzar,
            )

            return ResultadoAcuseRecibo(
                exito=estado
                in (
                    "enviado",
                    "aceptado",
                ),
                estado=estado,
                mensaje=mensaje,
                cude=datos.cude,
                error=respuesta_api.error,
            )

        except Exception as error:

            RepositorioFacturaCompra.actualizar_acuse_recibo(
                id_registro,
                estado="error",
                mensaje=str(error),
            )

            return ResultadoAcuseRecibo(
                estado="error",
                error=str(error),
            )
