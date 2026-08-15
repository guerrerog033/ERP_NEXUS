from __future__ import annotations

from types import SimpleNamespace

from aplicacion.framework.form.engine import FormEngine
from aplicacion.maestros.productos.producto_definition import (
    ProductoDefinition,
)
from aplicacion.maestros.productos.variantes_widget import (
    COL_EXISTENCIA,
    VariantesProductoWidget,
)


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def test_producto_form_engine_construye_campos_clave():
    _qapp()

    engine = FormEngine(
        ProductoDefinition,
    )

    engine.construir()

    for nombre in (
        "codigo",
        "nombre",
        "precio_venta",
        "stock_minimo",
        "existencia",
        "impuesto_venta_id",
        "maneja_variantes",
    ):
        assert engine.widget(
            nombre,
        ) is not None


def test_producto_form_engine_binding_carga_y_exporta():
    _qapp()

    engine = FormEngine(
        ProductoDefinition,
    )

    engine.construir()

    engine.cargar(
        SimpleNamespace(
            codigo="PRD010",
            nombre="Camiseta básica",
            tipo="producto",
            unidad_medida="Und",
            precio_venta=45000,
            precio_incluye_iva=False,
            costo=22000,
            existencia=12,
            stock_minimo=3,
            activo=True,
            maneja_variantes=False,
        ),
    )

    valores = engine.valores()

    assert valores["codigo"] == "PRD010"
    assert valores["nombre"] == "Camiseta Básica"
    assert valores["precio_venta"] == 45000
    assert valores["stock_minimo"] == 3
    assert valores["existencia"] == 12
    assert valores["activo"] is True


def test_producto_form_existencia_widget_solo_lectura():
    _qapp()

    engine = FormEngine(
        ProductoDefinition,
    )

    engine.construir()

    widget = engine.widget(
        "existencia",
    )

    assert widget.isEnabled() is False


def test_variantes_widget_existencia_solo_lectura():
    _qapp()

    widget = VariantesProductoWidget()

    widget._agregar_fila()

    existencia = widget._widget_celda(
        0,
        widget._indice_columna_fija(
            COL_EXISTENCIA,
        ),
    )

    assert existencia is not None
    assert existencia.isReadOnly() is True
