from __future__ import annotations

from unittest.mock import MagicMock, patch

from aplicacion.modulos.compras.integracion_oc import (
    ServicioIntegracionCompras,
)


def test_omitir_inventario_cuando_linea_recibida():

    db = MagicMock()
    factura = MagicMock()
    factura.orden_compra_id = 10

    detalle = MagicMock()
    detalle.cantidad = 5
    detalle.orden_detalle_id = 99
    detalle.producto_id = 1

    orden_detalle = MagicMock()
    orden_detalle.cantidad_recibida = 5

    query = MagicMock()
    query.filter.return_value = query
    query.first.return_value = orden_detalle
    db.query.return_value = query

    with patch.object(
        ServicioIntegracionCompras,
        "inventario_en_recepcion",
        return_value=True,
    ):

        assert ServicioIntegracionCompras.omitir_inventario_linea(
            db,
            factura,
            detalle,
        )


def test_no_omitir_inventario_sin_orden():

    db = MagicMock()
    factura = MagicMock()
    factura.orden_compra_id = None
    detalle = MagicMock()

    with patch.object(
        ServicioIntegracionCompras,
        "inventario_en_recepcion",
        return_value=True,
    ):

        assert not ServicioIntegracionCompras.omitir_inventario_linea(
            db,
            factura,
            detalle,
        )


@patch.object(
    ServicioIntegracionCompras,
    "_obtener_factura",
)
def test_evaluar_match_sin_vinculo(
    mock_obtener,
):

    factura = MagicMock()
    factura.orden_compra_id = None
    mock_obtener.return_value = factura

    resultado = ServicioIntegracionCompras.evaluar_match(
        1,
    )

    assert resultado.estado == "sin_vinculo"
