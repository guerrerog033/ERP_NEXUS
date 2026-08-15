"""Revisiones Alembic — Fase 4: Numeric en ventas/compras/tesorería."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from aplicacion.base_datos.alembic_numeric import (
    alterar_numeric,
)


revision: str = "0003_numeric_modulos"
down_revision: Union[str, None] = "0002_numeric_auditoria_campos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TABLAS_DINERO = {
    "proformas": [
        "subtotal",
        "total",
    ],
    "proforma_detalles": [
        "precio_unitario",
        "total_linea",
    ],
    "ordenes_pedido": [
        "subtotal",
        "total",
    ],
    "orden_pedido_detalles": [
        "precio_unitario",
        "total_linea",
    ],
    "remisiones_venta": [
        "subtotal",
        "total",
    ],
    "remision_venta_detalles": [
        "precio_unitario",
        "total_linea",
    ],
    "notas_credito_venta": [
        "subtotal",
        "iva",
        "valor_retefuente",
        "valor_reteica",
        "valor_reteiva",
        "total",
    ],
    "nota_credito_venta_detalles": [
        "precio_unitario",
        "total_linea",
    ],
    "notas_debito_venta": [
        "subtotal",
        "iva",
        "valor_retefuente",
        "valor_reteica",
        "valor_reteiva",
        "total",
    ],
    "nota_debito_venta_detalles": [
        "precio_unitario",
        "total_linea",
    ],
    "documentos_soporte": [
        "subtotal",
        "iva",
        "total",
    ],
    "documento_soporte_detalles": [
        "precio_unitario",
        "total_linea",
    ],
    "facturas_compra": [
        "subtotal",
        "iva",
        "valor_retefuente",
        "valor_reteica",
        "valor_reteiva",
        "total",
        "valor_pagado",
        "saldo_pendiente",
    ],
    "factura_compra_detalles": [
        "precio_unitario",
        "total_linea",
    ],
    "ordenes_compra": [
        "subtotal",
        "total",
    ],
    "orden_compra_detalles": [
        "precio_unitario",
        "total_linea",
    ],
    "recepcion_compra_detalles": [
        "costo_unitario",
    ],
    "cuentas_bancarias": [
        "saldo",
    ],
    "lotes_pago": [
        "total",
    ],
    "lote_pago_detalles": [
        "valor",
    ],
    "recibos_caja": [
        "total",
    ],
    "recibo_caja_detalles": [
        "valor",
    ],
    "comprobantes_egreso": [
        "total",
    ],
    "comprobante_egreso_detalles": [
        "valor",
    ],
    "extractos_bancarios": [
        "valor",
        "saldo",
    ],
    "conciliaciones_bancarias": [
        "valor",
    ],
}

_TABLAS_CANTIDAD = {
    "proforma_detalles": [
        "cantidad",
    ],
    "orden_pedido_detalles": [
        "cantidad",
    ],
    "remision_venta_detalles": [
        "cantidad",
    ],
    "nota_credito_venta_detalles": [
        "cantidad",
    ],
    "nota_debito_venta_detalles": [
        "cantidad",
    ],
    "documento_soporte_detalles": [
        "cantidad",
    ],
    "factura_compra_detalles": [
        "cantidad",
    ],
    "orden_compra_detalles": [
        "cantidad",
        "cantidad_recibida",
    ],
    "recepcion_compra_detalles": [
        "cantidad",
    ],
}

_TABLAS_PORCENTAJE = {
    "proforma_detalles": [
        "descuento_porcentaje",
    ],
}

_TABLAS_TASA = {
    "proformas": [
        "tasa_cambio",
    ],
}


def upgrade() -> None:

    for tabla, columnas in _TABLAS_DINERO.items():

        alterar_numeric(
            {
                tabla: columnas,
            },
            18,
            2,
        )

    for tabla, columnas in _TABLAS_CANTIDAD.items():

        alterar_numeric(
            {
                tabla: columnas,
            },
            18,
            4,
        )

    for tabla, columnas in _TABLAS_PORCENTAJE.items():

        alterar_numeric(
            {
                tabla: columnas,
            },
            8,
            4,
        )

    for tabla, columnas in _TABLAS_TASA.items():

        alterar_numeric(
            {
                tabla: columnas,
            },
            18,
            6,
        )


def downgrade() -> None:

    todas: dict[str, list[str]] = {}

    for origen in (
        _TABLAS_DINERO,
        _TABLAS_CANTIDAD,
        _TABLAS_PORCENTAJE,
        _TABLAS_TASA,
    ):

        for tabla, columnas in origen.items():

            todas.setdefault(
                tabla,
                [],
            ).extend(
                columnas,
            )

    for tabla, columnas in todas.items():

        for columna in columnas:

            op.alter_column(
                tabla,
                columna,
                type_=sa.Float(),
                postgresql_using=(
                    f"{columna}::double precision"
                ),
            )
