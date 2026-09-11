from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

pytestmark = pytest.mark.usefixtures(
    "qapp",
)


def test_enter_en_cantidad_avanza_el_foco(qtbot):
    from aplicacion.base_datos.registro_modelos import (
        importar_modelos,
    )

    importar_modelos()

    from aplicacion.modulos.compras.facturas.formulario import (
        COL_CANTIDAD,
        FormularioFacturaCompra,
    )

    form = FormularioFacturaCompra()
    qtbot.addWidget(form)
    form.show()

    spin_cantidad = form._widget_fila(
        0,
        COL_CANTIDAD,
    )

    assert spin_cantidad is not None

    editor = spin_cantidad.lineEdit()

    editor.setFocus()

    qtbot.keyClick(
        editor,
        Qt.Key.Key_Return,
    )

    assert form.focusWidget() is not editor


def test_enter_en_descripcion_avanza_el_foco(qtbot):
    from aplicacion.base_datos.registro_modelos import (
        importar_modelos,
    )

    importar_modelos()

    from aplicacion.modulos.compras.facturas.formulario import (
        COL_CANTIDAD,
        COL_DESCRIPCION,
        FormularioFacturaCompra,
    )

    form = FormularioFacturaCompra()
    qtbot.addWidget(form)
    form.show()
    qtbot.waitExposed(form)

    descripcion = form._widget_fila(
        0,
        COL_DESCRIPCION,
    )
    cantidad = form._widget_fila(
        0,
        COL_CANTIDAD,
    )

    descripcion.setFocus()
    qtbot.waitUntil(
        lambda: form.focusWidget() is descripcion,
    )

    qtbot.keyClick(
        descripcion,
        Qt.Key.Key_Return,
    )

    qtbot.waitUntil(
        lambda: form.focusWidget() is not descripcion,
    )

    assert form.focusWidget() in (
        cantidad,
        cantidad.lineEdit(),
    )


def test_foco_inicial_va_al_selector_de_proveedor(qtbot):
    from aplicacion.base_datos.registro_modelos import (
        importar_modelos,
    )

    importar_modelos()

    from aplicacion.modulos.compras.facturas.formulario import (
        FormularioFacturaCompra,
    )

    form = FormularioFacturaCompra()
    qtbot.addWidget(form)
    form.show()
    qtbot.waitExposed(form)

    qtbot.waitUntil(
        lambda: form.focusWidget() is form.proveedor.btn,
    )
