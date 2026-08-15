from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox


pytestmark = pytest.mark.usefixtures(
    "qapp",
)


def _factura_ui(
    *,
    estado: str = "borrador",
    contabilizado: bool = False,
):
    detalle = SimpleNamespace(
        descripcion="Producto demo",
        cantidad=1.0,
        precio_unitario=25000.0,
        total_linea=29750.0,
    )

    return SimpleNamespace(
        id=7,
        numero="FV-00007",
        estado=estado,
        estado_dian="",
        cufe="",
        fecha=date.today(),
        observaciones="",
        cliente_id=1,
        subtotal=25000.0,
        iva=4750.0,
        total=29750.0,
        saldo_pendiente=29750.0,
        contabilizado=contabilizado,
        inventario_aplicado=contabilizado,
        formato_impresion="estandar",
        detalles=[detalle],
    )


def _nota_credito_ui(
    *,
    estado: str = "borrador",
    contabilizado: bool = False,
):
    detalle = SimpleNamespace(
        descripcion="Producto demo",
        cantidad=1.0,
        total_linea=29750.0,
    )

    return SimpleNamespace(
        id=9,
        numero="NC-00009",
        estado=estado,
        estado_dian="",
        motivo="Devolución",
        cliente_id=1,
        factura_id=2,
        factura_cufe="CUFE-DEMO",
        subtotal=25000.0,
        iva=4750.0,
        total=29750.0,
        contabilizado=contabilizado,
        detalles=[detalle],
    )


def _nota_debito_ui(
    *,
    estado: str = "borrador",
    contabilizado: bool = False,
):
    detalle = SimpleNamespace(
        descripcion="Intereses",
        cantidad=1.0,
        total_linea=5950.0,
    )

    return SimpleNamespace(
        id=10,
        numero="ND-00010",
        estado=estado,
        estado_dian="",
        motivo="Intereses mora",
        cliente_id=1,
        factura_id=2,
        factura_cufe="CUFE-DEMO",
        subtotal=5000.0,
        iva=950.0,
        total=5950.0,
        contabilizado=contabilizado,
        detalles=[detalle],
    )


def _cliente_ui():
    return SimpleNamespace(
        razon_social="Cliente Demo",
        nombre_completo="Cliente Demo",
        nombre_comercial="Cliente Demo",
        numero_documento="900123456",
        dv=None,
        direccion="Calle 1",
        ciudad="Bogotá",
        telefono="6011234567",
        correo="demo@test.com",
    )


def _auto_confirmar(
    monkeypatch,
):
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: (
            QMessageBox.StandardButton.Yes
        ),
    )
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: None,
    )


def _stub_html_factura(
    monkeypatch,
):
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.facturas.vista_factura.generar_html_factura_venta",
        lambda *args, **kwargs: "<html></html>",
    )


def test_vista_factura_confirmar_invoca_servicio(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.facturas.datasource import (
        FacturaVentaDataSource,
    )
    from aplicacion.modulos.ventas.facturas.vista_factura import (
        VistaFacturaVenta,
    )

    factura = _factura_ui()

    mock_ds = MagicMock()
    mock_ds.obtener_completa.return_value = factura
    mock_ds.confirmar_venta.return_value = _factura_ui(
        estado="contabilizada",
        contabilizado=True,
    )

    monkeypatch.setattr(
        FacturaVentaDataSource,
        "obtener_completa",
        lambda self, _id: factura,
    )

    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    _auto_confirmar(
        monkeypatch,
    )
    _stub_html_factura(
        monkeypatch,
    )

    vista = VistaFacturaVenta(
        7,
    )
    vista.datasource = mock_ds
    vista._cargar_datos()

    assert vista.btn_confirmar.isEnabled()

    qtbot.mouseClick(
        vista.btn_confirmar,
        Qt.MouseButton.LeftButton,
    )

    mock_ds.confirmar_venta.assert_called_once_with(
        7,
        emitir_dian=False,
    )


def test_vista_nota_credito_confirmar_invoca_servicio(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.notas_credito.vista import (
        VistaNotaCreditoVenta,
    )

    nota = _nota_credito_ui()

    mock_ds = MagicMock()
    mock_ds.obtener_completa.return_value = nota
    mock_ds.confirmar_generacion.return_value = _nota_credito_ui(
        estado="contabilizada",
        contabilizado=True,
    )

    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    _auto_confirmar(
        monkeypatch,
    )

    vista = VistaNotaCreditoVenta(
        9,
    )
    vista.datasource = mock_ds
    vista._cargar_datos()

    assert vista.btn_confirmar.isEnabled()

    qtbot.mouseClick(
        vista.btn_confirmar,
        Qt.MouseButton.LeftButton,
    )

    mock_ds.confirmar_generacion.assert_called_once_with(
        9,
        emitir_dian=False,
    )


def test_vista_nota_debito_confirmar_invoca_servicio(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.notas_debito.vista import (
        VistaNotaDebitoVenta,
    )

    nota = _nota_debito_ui()

    mock_ds = MagicMock()
    mock_ds.obtener_completa.return_value = nota
    mock_ds.confirmar_generacion.return_value = _nota_debito_ui(
        estado="contabilizada",
        contabilizado=True,
    )

    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    _auto_confirmar(
        monkeypatch,
    )

    vista = VistaNotaDebitoVenta(
        10,
    )
    vista.datasource = mock_ds
    vista._cargar_datos()

    assert vista.btn_confirmar.isEnabled()

    qtbot.mouseClick(
        vista.btn_confirmar,
        Qt.MouseButton.LeftButton,
    )

    mock_ds.confirmar_generacion.assert_called_once_with(
        10,
        emitir_dian=False,
    )


def test_vista_nota_credito_cartera_invoca_resumen(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.cartera.servicios import (
        ServicioCartera,
    )
    from aplicacion.modulos.ventas.notas_credito.datasource import (
        NotaCreditoVentaDataSource,
    )
    from aplicacion.modulos.ventas.notas_credito.vista import (
        VistaNotaCreditoVenta,
    )

    nota = _nota_credito_ui(
        estado="contabilizada",
        contabilizado=True,
    )

    monkeypatch.setattr(
        NotaCreditoVentaDataSource,
        "obtener_completa",
        lambda self, _id: nota,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    monkeypatch.setattr(
        ServicioCartera,
        "resumen_cliente_cxc",
        MagicMock(
            return_value={
                "saldo_total": 15000.0,
                "saldo_vencido": 0.0,
                "facturas_pendientes": 1,
                "filas": [],
            },
        ),
    )
    _auto_confirmar(
        monkeypatch,
    )

    vista = VistaNotaCreditoVenta(
        9,
    )
    vista._cargar_datos()

    qtbot.mouseClick(
        vista.btn_cartera,
        Qt.MouseButton.LeftButton,
    )

    ServicioCartera.resumen_cliente_cxc.assert_called_once_with(
        1,
    )


def test_vista_nota_credito_ver_factura_abre_dialogo(
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.notas_credito.datasource import (
        NotaCreditoVentaDataSource,
    )
    from aplicacion.modulos.ventas.notas_credito.vista import (
        VistaNotaCreditoVenta,
    )

    nota = _nota_credito_ui(
        estado="contabilizada",
        contabilizado=True,
    )

    mock_dialogo = MagicMock()

    monkeypatch.setattr(
        NotaCreditoVentaDataSource,
        "obtener_completa",
        lambda self, _id: nota,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.facturas.servicios.ServicioFacturaVenta.obtener_completa",
        lambda _id: SimpleNamespace(
            id=2,
            numero="FV-00002",
        ),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.notas_credito.vista.mostrar_dialogo_vista",
        mock_dialogo,
    )

    vista = VistaNotaCreditoVenta(
        9,
    )
    vista._cargar_datos()

    vista._ver_factura_origen()

    mock_dialogo.assert_called_once()


def test_vista_nota_debito_cartera_invoca_resumen(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.cartera.servicios import (
        ServicioCartera,
    )
    from aplicacion.modulos.ventas.notas_debito.datasource import (
        NotaDebitoVentaDataSource,
    )
    from aplicacion.modulos.ventas.notas_debito.vista import (
        VistaNotaDebitoVenta,
    )

    nota = _nota_debito_ui(
        estado="contabilizada",
        contabilizado=True,
    )

    monkeypatch.setattr(
        NotaDebitoVentaDataSource,
        "obtener_completa",
        lambda self, _id: nota,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    monkeypatch.setattr(
        ServicioCartera,
        "resumen_cliente_cxc",
        MagicMock(
            return_value={
                "saldo_total": 15000.0,
                "saldo_vencido": 0.0,
                "facturas_pendientes": 1,
                "filas": [],
            },
        ),
    )
    _auto_confirmar(
        monkeypatch,
    )

    vista = VistaNotaDebitoVenta(
        10,
    )
    vista._cargar_datos()

    qtbot.mouseClick(
        vista.btn_cartera,
        Qt.MouseButton.LeftButton,
    )

    ServicioCartera.resumen_cliente_cxc.assert_called_once_with(
        1,
    )


def test_vista_factura_confirmar_deshabilitado_si_no_borrador(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.facturas.datasource import (
        FacturaVentaDataSource,
    )
    from aplicacion.modulos.ventas.facturas.vista_factura import (
        VistaFacturaVenta,
    )

    factura = _factura_ui(
        estado="contabilizada",
        contabilizado=True,
    )

    mock_ds = MagicMock()
    mock_ds.obtener_completa.return_value = factura

    monkeypatch.setattr(
        FacturaVentaDataSource,
        "obtener_completa",
        lambda self, _id: factura,
    )

    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    _stub_html_factura(
        monkeypatch,
    )

    vista = VistaFacturaVenta(
        7,
    )
    vista.datasource = mock_ds
    vista._cargar_datos()

    assert not vista.btn_confirmar.isEnabled()


def test_vista_nota_credito_confirmar_deshabilitado_si_no_borrador(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.notas_credito.vista import (
        VistaNotaCreditoVenta,
    )

    nota = _nota_credito_ui(
        estado="contabilizada",
        contabilizado=True,
    )

    mock_ds = MagicMock()
    mock_ds.obtener_completa.return_value = nota

    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )

    vista = VistaNotaCreditoVenta(
        9,
    )
    vista.datasource = mock_ds
    vista._cargar_datos()

    assert not vista.btn_confirmar.isEnabled()


def _pedido_ui(
    *,
    estado: str = "borrador",
):
    detalle = SimpleNamespace(
        descripcion="Producto demo",
        cantidad=1.0,
        precio_unitario=25000.0,
        total_linea=29750.0,
    )

    return SimpleNamespace(
        id=11,
        numero="PED-00011",
        estado=estado,
        cliente_id=1,
        reserva_aplicada=False,
        subtotal=25000.0,
        total=29750.0,
        detalles=[detalle],
    )


def _remision_ui(
    *,
    estado: str = "borrador",
    inventario_aplicado: bool = False,
):
    detalle = SimpleNamespace(
        descripcion="Producto demo",
        cantidad=1.0,
        precio_unitario=25000.0,
        total_linea=29750.0,
    )

    return SimpleNamespace(
        id=12,
        numero="REM-00012",
        estado=estado,
        cliente_id=1,
        inventario_aplicado=inventario_aplicado,
        subtotal=25000.0,
        total=29750.0,
        detalles=[detalle],
    )


def test_vista_pedido_confirmar_invoca_servicio(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.pedidos.datasource import (
        PedidoDataSource,
    )
    from aplicacion.modulos.ventas.pedidos.vista_pedido import (
        VistaPedido,
    )

    pedido = _pedido_ui()

    mock_ds = MagicMock()
    mock_ds.obtener_completa.return_value = pedido
    mock_ds.confirmar_pedido.return_value = _pedido_ui(
        estado="pendiente",
    )

    monkeypatch.setattr(
        PedidoDataSource,
        "obtener_completa",
        lambda self, _id: pedido,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.pedidos.vista_pedido.generar_html_pedido",
        lambda *args, **kwargs: "<html></html>",
    )
    _auto_confirmar(
        monkeypatch,
    )

    vista = VistaPedido(
        11,
    )
    vista.datasource = mock_ds
    vista._cargar_datos()

    assert vista.btn_confirmar.isEnabled()
    assert not vista.btn_facturar.isEnabled()

    qtbot.mouseClick(
        vista.btn_confirmar,
        Qt.MouseButton.LeftButton,
    )

    mock_ds.confirmar_pedido.assert_called_once_with(
        11,
    )


def test_vista_remision_confirmar_invoca_servicio(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.remisiones.datasource import (
        RemisionDataSource,
    )
    from aplicacion.modulos.ventas.remisiones.vista_remision import (
        VistaRemision,
    )

    remision = _remision_ui()

    mock_ds = MagicMock()
    mock_ds.obtener_completa.return_value = remision
    mock_ds.confirmar_remision.return_value = _remision_ui(
        estado="pendiente",
    )

    monkeypatch.setattr(
        RemisionDataSource,
        "obtener_completa",
        lambda self, _id: remision,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.guias_remision.servicios.ServicioGuiaRemisionElectronica.obtener_por_remision",
        lambda _id: None,
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.guias_remision.servicios.ServicioGuiaRemisionElectronica.guia_emitida_para_remision",
        lambda _id: False,
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.guias_remision.servicios.ServicioGuiaRemisionElectronica.exigir_guia_emitida_logistica",
        lambda: False,
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.remisiones.vista_remision.generar_html_remision",
        lambda *args, **kwargs: "<html></html>",
    )
    _auto_confirmar(
        monkeypatch,
    )

    vista = VistaRemision(
        12,
    )
    vista.datasource = mock_ds
    vista._cargar_datos()

    assert vista.btn_confirmar.isEnabled()
    assert not vista.btn_despachar.isEnabled()

    qtbot.mouseClick(
        vista.btn_confirmar,
        Qt.MouseButton.LeftButton,
    )

    mock_ds.confirmar_remision.assert_called_once_with(
        12,
    )


def test_vista_remision_cartera_invoca_resumen(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.cartera.servicios import (
        ServicioCartera,
    )
    from aplicacion.modulos.ventas.remisiones.datasource import (
        RemisionDataSource,
    )
    from aplicacion.modulos.ventas.remisiones.vista_remision import (
        VistaRemision,
    )

    remision = _remision_ui(
        estado="pendiente",
    )

    monkeypatch.setattr(
        RemisionDataSource,
        "obtener_completa",
        lambda self, _id: remision,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.guias_remision.servicios.ServicioGuiaRemisionElectronica.obtener_por_remision",
        lambda _id: None,
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.guias_remision.servicios.ServicioGuiaRemisionElectronica.guia_emitida_para_remision",
        lambda _id: False,
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.guias_remision.servicios.ServicioGuiaRemisionElectronica.exigir_guia_emitida_logistica",
        lambda: False,
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.remisiones.vista_remision.generar_html_remision",
        lambda *args, **kwargs: "<html></html>",
    )
    monkeypatch.setattr(
        ServicioCartera,
        "resumen_cliente_cxc",
        MagicMock(
            return_value={
                "saldo_total": 29750.0,
                "saldo_vencido": 0.0,
                "facturas_pendientes": 1,
                "filas": [],
            },
        ),
    )
    _auto_confirmar(
        monkeypatch,
    )

    vista = VistaRemision(
        12,
    )
    vista._cargar_datos()

    qtbot.mouseClick(
        vista.btn_cartera,
        Qt.MouseButton.LeftButton,
    )

    ServicioCartera.resumen_cliente_cxc.assert_called_once_with(
        1,
    )


def _cotizacion_ui(
    *,
    estado: str = "borrador",
):
    detalle = SimpleNamespace(
        descripcion="Producto demo",
        cantidad=1.0,
        precio_unitario=25000.0,
        total_linea=29750.0,
    )

    return SimpleNamespace(
        id=3,
        numero="COT-00003",
        estado=estado,
        cliente_id=1,
        observaciones="",
        subtotal=25000.0,
        iva=4750.0,
        total=29750.0,
        formato_impresion="clasica",
        detalles=[detalle],
    )


def test_vista_cotizacion_confirmar_invoca_servicio(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.cotizaciones.datasource import (
        CotizacionDataSource,
    )
    from aplicacion.modulos.ventas.cotizaciones.vista_cotizacion import (
        VistaCotizacion,
    )

    cotizacion = _cotizacion_ui()

    mock_ds = MagicMock()
    mock_ds.obtener_completa.return_value = cotizacion
    mock_ds.confirmar_cotizacion.return_value = _cotizacion_ui(
        estado="aprobada",
    )

    monkeypatch.setattr(
        CotizacionDataSource,
        "obtener_completa",
        lambda self, _id: cotizacion,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.cotizaciones.vista_cotizacion.generar_html_cotizacion",
        lambda *args, **kwargs: "<html></html>",
    )
    _auto_confirmar(
        monkeypatch,
    )

    vista = VistaCotizacion(
        3,
    )
    vista.datasource = mock_ds
    vista._cargar_datos()

    assert vista.btn_confirmar.isEnabled()
    assert not vista.btn_facturar.isEnabled()

    qtbot.mouseClick(
        vista.btn_confirmar,
        Qt.MouseButton.LeftButton,
    )

    mock_ds.confirmar_cotizacion.assert_called_once_with(
        3,
    )


def test_vista_cotizacion_confirmar_deshabilitado_si_aprobada(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.cotizaciones.datasource import (
        CotizacionDataSource,
    )
    from aplicacion.modulos.ventas.cotizaciones.vista_cotizacion import (
        VistaCotizacion,
    )

    cotizacion = _cotizacion_ui(
        estado="aprobada",
    )

    monkeypatch.setattr(
        CotizacionDataSource,
        "obtener_completa",
        lambda self, _id: cotizacion,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.cotizaciones.vista_cotizacion.generar_html_cotizacion",
        lambda *args, **kwargs: "<html></html>",
    )

    vista = VistaCotizacion(
        3,
    )
    vista._cargar_datos()

    assert not vista.btn_confirmar.isEnabled()
    assert vista.btn_facturar.isEnabled()


def test_vista_cotizacion_estado_cuenta_invoca_dialogo(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.cotizaciones.datasource import (
        CotizacionDataSource,
    )
    from aplicacion.modulos.ventas.cotizaciones.vista_cotizacion import (
        VistaCotizacion,
    )

    cotizacion = _cotizacion_ui(
        estado="aprobada",
    )

    monkeypatch.setattr(
        CotizacionDataSource,
        "obtener_completa",
        lambda self, _id: cotizacion,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.cotizaciones.vista_cotizacion.generar_html_cotizacion",
        lambda *args, **kwargs: "<html></html>",
    )

    mock_estado_cuenta = MagicMock()
    monkeypatch.setattr(
        "aplicacion.modulos.cartera.ui_comercial.mostrar_estado_cuenta_cliente",
        mock_estado_cuenta,
    )

    vista = VistaCotizacion(
        3,
    )
    vista._cargar_datos()

    qtbot.mouseClick(
        vista.btn_estado_cuenta,
        Qt.MouseButton.LeftButton,
    )

    mock_estado_cuenta.assert_called_once_with(
        vista,
        1,
        nombre_cliente="Cliente Demo",
    )


def test_vista_cotizacion_cartera_invoca_resumen(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.cartera.servicios import (
        ServicioCartera,
    )
    from aplicacion.modulos.ventas.cotizaciones.datasource import (
        CotizacionDataSource,
    )
    from aplicacion.modulos.ventas.cotizaciones.vista_cotizacion import (
        VistaCotizacion,
    )

    cotizacion = _cotizacion_ui(
        estado="aprobada",
    )

    monkeypatch.setattr(
        CotizacionDataSource,
        "obtener_completa",
        lambda self, _id: cotizacion,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.cotizaciones.vista_cotizacion.generar_html_cotizacion",
        lambda *args, **kwargs: "<html></html>",
    )
    monkeypatch.setattr(
        ServicioCartera,
        "resumen_cliente_cxc",
        MagicMock(
            return_value={
                "saldo_total": 29750.0,
                "saldo_vencido": 0.0,
                "facturas_pendientes": 1,
                "filas": [],
            },
        ),
    )
    _auto_confirmar(
        monkeypatch,
    )

    vista = VistaCotizacion(
        3,
    )
    vista._cargar_datos()

    qtbot.mouseClick(
        vista.btn_cartera,
        Qt.MouseButton.LeftButton,
    )

    ServicioCartera.resumen_cliente_cxc.assert_called_once_with(
        1,
    )


def test_vista_factura_estado_cuenta_usa_helper(
    qtbot,
    monkeypatch,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.facturas.datasource import (
        FacturaVentaDataSource,
    )
    from aplicacion.modulos.ventas.facturas.vista_factura import (
        VistaFacturaVenta,
    )

    factura = _factura_ui(
        estado="confirmada",
        contabilizado=True,
    )

    monkeypatch.setattr(
        FacturaVentaDataSource,
        "obtener_completa",
        lambda self, _id: factura,
    )
    monkeypatch.setattr(
        TerceroServicio,
        "obtener_por_id",
        lambda _id: _cliente_ui(),
    )
    _stub_html_factura(
        monkeypatch,
    )

    mock_estado = MagicMock()
    monkeypatch.setattr(
        "aplicacion.modulos.cartera.ui_comercial.estado_cuenta_desde_documento",
        mock_estado,
    )

    vista = VistaFacturaVenta(
        7,
    )
    vista._cargar_datos()

    qtbot.mouseClick(
        vista.btn_estado_cuenta,
        Qt.MouseButton.LeftButton,
    )

    mock_estado.assert_called_once_with(
        vista,
        factura,
        nombre_cliente="Cliente Demo",
    )
