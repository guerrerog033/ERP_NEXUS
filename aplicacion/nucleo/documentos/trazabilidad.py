"""Registra vínculos al crear documentos derivados."""

from __future__ import annotations

from . import tipos as T
from .vinculos import DocumentoVinculoRepositorio


def vincular(
    tipo_origen: str,
    documento_origen_id: int,
    tipo_destino: str,
    documento_destino_id: int,
) -> None:

    if not documento_origen_id or not documento_destino_id:

        return

    DocumentoVinculoRepositorio.registrar(
        tipo_origen,
        documento_origen_id,
        tipo_destino,
        documento_destino_id,
    )


def vincular_cotizacion_pedido(
    cotizacion_id: int,
    pedido_id: int,
) -> None:

    vincular(
        T.COTIZACION,
        cotizacion_id,
        T.PEDIDO_VENTA,
        pedido_id,
    )


def vincular_pedido_remision(
    pedido_id: int,
    remision_id: int,
) -> None:

    vincular(
        T.PEDIDO_VENTA,
        pedido_id,
        T.REMISION,
        remision_id,
    )


def vincular_pedido_factura(
    pedido_id: int,
    factura_id: int,
) -> None:

    vincular(
        T.PEDIDO_VENTA,
        pedido_id,
        T.FACTURA_VENTA,
        factura_id,
    )


def vincular_cotizacion_factura(
    cotizacion_id: int,
    factura_id: int,
) -> None:

    vincular(
        T.COTIZACION,
        cotizacion_id,
        T.FACTURA_VENTA,
        factura_id,
    )


def vincular_remision_factura(
    remision_id: int,
    factura_id: int,
) -> None:

    vincular(
        T.REMISION,
        remision_id,
        T.FACTURA_VENTA,
        factura_id,
    )


def vincular_cotizacion_remision(
    cotizacion_id: int,
    remision_id: int,
) -> None:

    vincular(
        T.COTIZACION,
        cotizacion_id,
        T.REMISION,
        remision_id,
    )
