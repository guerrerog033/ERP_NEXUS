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

    from aplicacion.modulos.ventas.facturas.formulario import (
        COL_CANTIDAD,
        FormularioFacturaVenta,
    )

    form = FormularioFacturaVenta()
    qtbot.addWidget(form)
    form.show()

    spin_cantidad = form._widget_celda(
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
