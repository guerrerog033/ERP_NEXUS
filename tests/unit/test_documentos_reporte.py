from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

from aplicacion.modulos.ventas.pedidos.formatos_impresion import (
    generar_html_pedido,
)
from aplicacion.modulos.compras.ordenes.formatos_impresion import (
    generar_html_orden_compra,
)
from aplicacion.modulos.tesoreria.recibos_caja.formatos_impresion import (
    generar_html_recibo,
)
from aplicacion.reportes.comunes.html_documento import (
    contexto_formato_desde_dto,
)
from aplicacion.reportes.ventas.pedido import (
    crear_reporte_pedido,
)


def _pedido_mock():

    pedido = MagicMock()
    pedido.numero = "PED-0001"
    pedido.fecha = date(
        2026,
        8,
        10,
    )
    pedido.subtotal = 100000
    pedido.total = 100000
    pedido.estado = "pendiente"
    pedido.observaciones = ""
    pedido.vendedor = "Juan"
    pedido.cotizacion_id = None
    pedido.cliente_id = 1

    return pedido


@patch(
    "aplicacion.modulos.ventas.pedidos.formatos_impresion.generar_html_desde_contexto",
    return_value="<html>PEDIDO</html>",
)
@patch(
    "aplicacion.modulos.ventas.pedidos.formatos_impresion.contexto_formato_desde_dto",
    wraps=contexto_formato_desde_dto,
)
def test_generar_html_pedido_usa_dto(
    mock_ctx,
    mock_gen,
):

    html = generar_html_pedido(
        _pedido_mock(),
        [],
        "Cliente Demo",
    )

    assert html == "<html>PEDIDO</html>"
    mock_ctx.assert_called_once()
    mock_gen.assert_called_once()


def test_crear_reporte_pedido():

    reporte = crear_reporte_pedido(
        _pedido_mock(),
        [],
        "Cliente Demo",
    )

    assert reporte.numero_documento == "PED-0001"


@patch(
    "aplicacion.modulos.compras.ordenes.formatos_impresion._datos_empresa",
    return_value={
        "nombre": "Empresa",
        "nit": "900",
    },
)
def test_generar_html_orden_compra(
    *_mocks,
):

    orden = MagicMock()
    orden.numero = "OC-001"
    orden.fecha = date(
        2026,
        8,
        10,
    )
    orden.estado = "pendiente"
    orden.subtotal = 50000
    orden.total = 50000
    orden.observaciones = ""

    html = generar_html_orden_compra(
        orden,
        [],
        "Proveedor XYZ",
    )

    assert "ORDEN DE COMPRA" in html
    assert "OC-001" in html


@patch(
    "aplicacion.modulos.tesoreria.recibos_caja.formatos_impresion.recibo_caja_a_dto",
)
@patch(
    "aplicacion.modulos.tesoreria.recibos_caja.formatos_impresion.html_comercial_desde_dto",
    return_value="<html>RECIBO</html>",
)
def test_generar_html_recibo_caja_usa_dto(
    mock_html,
    mock_dto,
):

    mock_dto.return_value = {
        "numero": "RC-001",
        "fecha": "10/08/2026",
        "valor": 1250000,
        "cliente": {
            "nombre": "Cliente ABC",
        },
        "lineas": [],
    }

    recibo = MagicMock()
    recibo.numero = "RC-001"
    recibo.fecha = date(
        2026,
        8,
        10,
    )
    recibo.estado = "aplicado"
    recibo.forma_pago = "Transferencia"
    recibo.valor_total = 1250000
    recibo.observaciones = ""
    recibo.detalles = []

    html = generar_html_recibo(
        recibo,
        nombre_cliente="Cliente ABC",
    )

    assert html == "<html>RECIBO</html>"
    mock_dto.assert_called_once()
    mock_html.assert_called_once()
