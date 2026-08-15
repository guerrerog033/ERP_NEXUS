from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from aplicacion.modulos.ventas.facturas.servicios import (
    ServicioFacturaVenta,
)
from aplicacion.modulos.ventas.pedidos.servicios import (
    ServicioPedido,
)
from aplicacion.modulos.ventas.remisiones.servicios import (
    ServicioRemision,
)


def _remision_mock(
    *,
    remision_id: int = 20,
    cotizacion_id: int = 10,
    cliente_id: int = 5,
    pedido_id: int | None = None,
):
    detalle = SimpleNamespace(
        producto_id=99,
        producto_variante_id=None,
        descripcion="Producto demo",
        cantidad=2.0,
        precio_unitario=10000.0,
        impuesto_id=1,
        precio_incluye_iva=False,
        total_linea=23800.0,
    )

    return SimpleNamespace(
        id=remision_id,
        cotizacion_id=cotizacion_id,
        pedido_id=pedido_id,
        cliente_id=cliente_id,
        observaciones="Remisión demo",
        total=23800.0,
        detalles=[detalle],
    )

def _cotizacion_mock(
    *,
    cotizacion_id: int = 10,
    cliente_id: int = 5,
):
    detalle = SimpleNamespace(
        producto_id=99,
        producto_variante_id=None,
        descripcion="Producto demo",
        cantidad=2.0,
        precio_unitario=10000.0,
        impuesto_id=1,
        precio_incluye_iva=False,
        total_linea=23800.0,
    )

    return SimpleNamespace(
        id=cotizacion_id,
        cliente_id=cliente_id,
        observaciones="Cotización demo",
        vendedor="Vendedor Demo",
        subtotal=20000.0,
        total=23800.0,
        retefuente_id=None,
        reteica_id=None,
        reteiva_id=None,
        estado="aprobada",
        formato_impresion="clasica",
        detalles=[detalle],
    )


@patch.object(
    ServicioFacturaVenta.repositorio,
    "obtener_por_cotizacion",
    return_value=None,
)
@patch.object(
    ServicioFacturaVenta.repositorio,
    "siguiente_secuencia",
    return_value=42,
)
@patch.object(
    ServicioFacturaVenta.repositorio,
    "guardar_completa",
)
@patch(
    "aplicacion.modulos.ventas.facturas.servicios.ServicioCotizacion.obtener_completa",
)
def test_crear_factura_desde_cotizacion_copia_cliente_y_lineas(
    mock_obtener_cotizacion,
    mock_guardar,
    _mock_secuencia,
    _mock_existente,
):
    cotizacion = _cotizacion_mock()

    mock_obtener_cotizacion.return_value = cotizacion

    factura_guardada = MagicMock(
        id=100,
        cotizacion_id=10,
        cliente_id=5,
    )

    mock_guardar.return_value = factura_guardada

    resultado = ServicioFacturaVenta.crear_desde_cotizacion(
        10,
    )

    assert resultado is factura_guardada

    cabecera, lineas = mock_guardar.call_args[0]

    assert cabecera["cliente_id"] == 5
    assert cabecera["cotizacion_id"] == 10
    assert cabecera["estado"] == "borrador"
    assert len(lineas) == 1
    assert lineas[0]["producto_id"] == 99
    assert lineas[0]["cantidad"] == 2.0
    assert lineas[0]["precio_unitario"] == 10000.0


@patch.object(
    ServicioFacturaVenta.repositorio,
    "obtener_por_cotizacion",
)
def test_crear_factura_desde_cotizacion_rechaza_duplicado(
    mock_existente,
):
    mock_existente.return_value = SimpleNamespace(
        numero="FV-00001",
    )

    with pytest.raises(
        ValueError,
        match="ya tiene la factura",
    ):
        ServicioFacturaVenta.crear_desde_cotizacion(
            10,
        )


@patch.object(
    ServicioPedido.repositorio,
    "obtener_por_cotizacion",
    return_value=None,
)
@patch.object(
    ServicioPedido.repositorio,
    "guardar_completa",
)
@patch(
    "aplicacion.modulos.ventas.pedidos.servicios.ServicioCotizacion.obtener_completa",
)
def test_crear_pedido_desde_cotizacion_copia_totales(
    mock_obtener_cotizacion,
    mock_guardar,
    _mock_existente,
):
    cotizacion = _cotizacion_mock()

    mock_obtener_cotizacion.return_value = cotizacion

    pedido_guardado = MagicMock(
        id=50,
        cotizacion_id=10,
    )

    mock_guardar.return_value = pedido_guardado

    resultado = ServicioPedido.crear_desde_cotizacion(
        10,
    )

    assert resultado is pedido_guardado

    cabecera, lineas = mock_guardar.call_args[0]

    assert cabecera["cotizacion_id"] == 10
    assert cabecera["cliente_id"] == 5
    assert cabecera["subtotal"] == 20000.0
    assert cabecera["total"] == 23800.0
    assert cabecera["estado"] == "borrador"
    assert cabecera["fecha"] == date.today()
    assert len(lineas) == 1


@patch.object(
    ServicioPedido.repositorio,
    "obtener_por_cotizacion",
)
def test_crear_pedido_desde_cotizacion_rechaza_duplicado(
    mock_existente,
):
    mock_existente.return_value = SimpleNamespace(
        numero="PD-00001",
    )

    with pytest.raises(
        ValueError,
        match="ya tiene el pedido",
    ):
        ServicioPedido.crear_desde_cotizacion(
            10,
        )


@patch.object(
    ServicioRemision.repositorio,
    "obtener_por_cotizacion",
    return_value=None,
)
@patch.object(
    ServicioRemision.repositorio,
    "guardar_completa",
)
@patch(
    "aplicacion.modulos.ventas.remisiones.servicios.ServicioCotizacion.obtener_completa",
)
def test_crear_remision_desde_cotizacion_copia_cliente(
    mock_obtener_cotizacion,
    mock_guardar,
    _mock_existente,
):
    cotizacion = _cotizacion_mock()

    mock_obtener_cotizacion.return_value = cotizacion

    remision_guardada = MagicMock(
        id=60,
        cotizacion_id=10,
        cliente_id=5,
    )

    mock_guardar.return_value = remision_guardada

    resultado = ServicioRemision.crear_desde_cotizacion(
        10,
    )

    assert resultado is remision_guardada

    cabecera, lineas = mock_guardar.call_args[0]

    assert cabecera["cotizacion_id"] == 10
    assert cabecera["cliente_id"] == 5
    assert cabecera["estado"] == "borrador"
    assert cabecera["fecha"] == date.today()
    assert len(lineas) == 1


@patch.object(
    ServicioRemision.repositorio,
    "obtener_por_cotizacion",
)
def test_crear_remision_desde_cotizacion_rechaza_duplicado(
    mock_existente,
):
    mock_existente.return_value = SimpleNamespace(
        numero="RM-00001",
    )

    with pytest.raises(
        ValueError,
        match="ya tiene la remisión",
    ):
        ServicioRemision.crear_desde_cotizacion(
            10,
        )


@patch.object(
    ServicioFacturaVenta.repositorio,
    "obtener_por_cotizacion",
    return_value=None,
)
@patch.object(
    ServicioFacturaVenta.repositorio,
    "siguiente_secuencia",
    return_value=43,
)
@patch.object(
    ServicioFacturaVenta.repositorio,
    "guardar_completa",
)
@patch(
    "aplicacion.modulos.ventas.remisiones.servicios.ServicioRemision.obtener_completa",
)
def test_crear_factura_desde_remision_copia_cliente_y_lineas(
    mock_obtener_remision,
    mock_guardar,
    _mock_secuencia,
    _mock_existente,
):
    remision = _remision_mock()

    mock_obtener_remision.return_value = remision

    factura_guardada = MagicMock(
        id=110,
        cotizacion_id=10,
        cliente_id=5,
    )

    mock_guardar.return_value = factura_guardada

    resultado = ServicioFacturaVenta.crear_desde_remision(
        20,
    )

    assert resultado is factura_guardada

    cabecera, lineas = mock_guardar.call_args[0]

    assert cabecera["cliente_id"] == 5
    assert cabecera["cotizacion_id"] == 10
    assert cabecera["estado"] == "borrador"
    assert len(lineas) == 1
    assert lineas[0]["producto_id"] == 99


@patch(
    "aplicacion.modulos.ventas.remisiones.servicios.ServicioRemision.obtener_completa",
)
@patch.object(
    ServicioFacturaVenta.repositorio,
    "obtener_por_cotizacion",
)
def test_crear_factura_desde_remision_rechaza_duplicado(
    mock_existente,
    mock_obtener_remision,
):
    mock_obtener_remision.return_value = _remision_mock()
    mock_existente.return_value = SimpleNamespace(
        numero="FV-00001",
    )

    with pytest.raises(
        ValueError,
        match="Ya existe la factura",
    ):
        ServicioFacturaVenta.crear_desde_remision(
            20,
        )


@patch.object(
    ServicioPedido.repositorio,
    "actualizar_estado_confirmacion",
)
@patch.object(
    ServicioPedido,
    "obtener_completa",
)
def test_confirmar_pedido_borrador_a_pendiente(
    mock_obtener,
    mock_actualizar,
):
    from aplicacion.modulos.ventas.pedidos.integracion import (
        IntegracionPedido,
    )

    pedido_borrador = SimpleNamespace(
        id=5,
        estado="borrador",
    )
    pedido_pendiente = SimpleNamespace(
        id=5,
        estado="pendiente",
    )

    mock_obtener.side_effect = [
        pedido_borrador,
        pedido_pendiente,
    ]
    mock_actualizar.return_value = pedido_pendiente

    resultado = IntegracionPedido.confirmar_pedido(
        5,
    )

    assert resultado.estado == "pendiente"
    mock_actualizar.assert_called_once_with(
        5,
        estado="pendiente",
    )


@patch.object(
    ServicioFacturaVenta.repositorio,
    "obtener_por_cotizacion",
    return_value=None,
)
@patch(
    "aplicacion.modulos.ventas.facturas.servicios.ServicioCotizacion.obtener_completa",
)
def test_crear_factura_desde_cotizacion_rechaza_borrador(
    mock_obtener_cotizacion,
    _mock_existente,
):
    cotizacion = _cotizacion_mock(
        cotizacion_id=10,
    )
    cotizacion.estado = "borrador"

    mock_obtener_cotizacion.return_value = cotizacion

    with pytest.raises(
        ValueError,
        match="Confirme la cotización",
    ):
        ServicioFacturaVenta.crear_desde_cotizacion(
            10,
        )


@patch(
    "aplicacion.modulos.ventas.cotizaciones.integracion.RepositorioCotizacion.actualizar_estado_confirmacion",
)
@patch(
    "aplicacion.modulos.ventas.cotizaciones.integracion.ServicioCotizacion.obtener_completa",
)
def test_confirmar_cotizacion_borrador_a_aprobada(
    mock_obtener,
    mock_actualizar,
):
    from aplicacion.modulos.ventas.cotizaciones.integracion import (
        IntegracionCotizacion,
    )

    cotizacion_borrador = _cotizacion_mock()
    cotizacion_borrador.estado = "borrador"
    cotizacion_aprobada = _cotizacion_mock()
    cotizacion_aprobada.estado = "aprobada"

    mock_obtener.side_effect = [
        cotizacion_borrador,
        cotizacion_aprobada,
    ]
    mock_actualizar.return_value = cotizacion_aprobada

    resultado = IntegracionCotizacion.confirmar_cotizacion(
        10,
    )

    assert resultado.estado == "aprobada"
    mock_actualizar.assert_called_once_with(
        10,
        estado="aprobada",
    )


@patch(
    "aplicacion.modulos.ventas.cotizaciones.integracion.ServicioCotizacion.obtener_completa",
)
def test_confirmar_cotizacion_rechaza_si_no_borrador(
    mock_obtener,
):
    from aplicacion.modulos.ventas.cotizaciones.integracion import (
        IntegracionCotizacion,
    )

    mock_obtener.return_value = _cotizacion_mock(
        cotizacion_id=10,
    )

    with pytest.raises(
        ValueError,
        match="ya fue confirmada",
    ):
        IntegracionCotizacion.confirmar_cotizacion(
            10,
        )
