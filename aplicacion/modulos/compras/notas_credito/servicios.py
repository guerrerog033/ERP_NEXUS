from __future__ import annotations

from datetime import date

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.nucleo.configuracion import Configuracion

from .repositorio import RepositorioNotaCreditoCompra


MOTIVOS_NOTA_CREDITO_COMPRA = (
    "Devolución de bienes al proveedor",
    "Rebaja o descuento recibido",
    "Anulación parcial de factura",
    "Ajuste de precio",
    "Otros",
)


class ServicioNotaCreditoCompra(ServicioBase):

    repositorio = RepositorioNotaCreditoCompra

    entidad_auditoria = "NotaCreditoCompra"

    modulo_auditoria = "compras/notas_credito"

    PREFIJO = "NCC"

    LONGITUD = 6

    @classmethod
    def generar_numero(cls) -> str:

        from aplicacion.nucleo.numeracion.servicio import (
            ServicioNumeracion,
        )

        prefijo = str(
            Configuracion.obtener(
                "compras",
                "prefijo_nota_credito",
            )
            or cls.PREFIJO,
        )

        longitud = int(
            Configuracion.obtener(
                "compras",
                "longitud_secuencia",
            )
            or cls.LONGITUD,
        )

        return ServicioNumeracion.siguiente_numero(
            "nota_credito_compra",
            prefijo,
            longitud=longitud,
            consecutivo_minimo=(
                cls.repositorio.siguiente_secuencia(prefijo) - 1
            ),
        )

    @classmethod
    def listar_facturas_contabilizadas(
        cls,
        limite: int = 50,
    ):

        return cls.repositorio.listar_facturas_contabilizadas(
            limite,
        )

    @classmethod
    def crear_desde_factura(
        cls,
        factura_id: int,
        motivo: str | None = None,
    ):

        from aplicacion.modulos.compras.facturas.servicios import (
            ServicioFacturaCompra,
        )

        factura = ServicioFacturaCompra.obtener_completa(
            factura_id,
        )

        if factura is None:

            raise ValueError(
                "No se encontró la factura de compra.",
            )

        if not factura.contabilizado:

            raise ValueError(
                "La factura debe estar contabilizada.",
            )

        if not factura.proveedor_id:

            raise ValueError(
                "La factura no tiene proveedor.",
            )

        lineas = [
            {
                "producto_id": detalle.producto_id,
                "producto_variante_id": (
                    detalle.producto_variante_id
                ),
                "descripcion": detalle.descripcion,
                "cantidad": detalle.cantidad,
                "precio_unitario": (
                    detalle.precio_unitario
                ),
                "impuesto_id": detalle.impuesto_id,
                "precio_incluye_iva": (
                    detalle.precio_incluye_iva
                ),
                "total_linea": detalle.total_linea,
            }
            for detalle in factura.detalles
        ]

        cabecera = {
            "numero": cls.generar_numero(),
            "fecha": date.today(),
            "proveedor_id": factura.proveedor_id,
            "factura_compra_id": factura.id,
            "motivo": (
                motivo
                or MOTIVOS_NOTA_CREDITO_COMPRA[0]
            ),
            "factura_cufe": factura.cufe,
            "observaciones": (
                f"Devolución factura {factura.numero}"
            ),
            "estado": "borrador",
            "activo": True,
        }

        ServicioFacturaCompra._aplicar_resumen(
            cabecera,
            lineas,
        )

        return cls.repositorio.guardar_completa(
            cabecera,
            lineas,
        )

    @classmethod
    def obtener_completa(
        cls,
        id_registro: int,
    ):

        return cls.repositorio.obtener_completa(
            id_registro,
        )
