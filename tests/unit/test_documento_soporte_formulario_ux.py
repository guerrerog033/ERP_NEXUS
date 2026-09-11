from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

pytestmark = pytest.mark.usefixtures(
    "qapp",
)


def test_enter_en_cantidad_avanza_a_precio(qtbot):
    from aplicacion.base_datos.registro_modelos import (
        importar_modelos,
    )

    importar_modelos()

    from aplicacion.modulos.compras.documentos_soporte.formulario import (
        COL_CANTIDAD,
        COL_PRECIO,
        FormularioDocumentoSoporte,
    )

    form = FormularioDocumentoSoporte()
    qtbot.addWidget(form)
    form.show()
    qtbot.waitExposed(form)

    cantidad = form.tabla.cellWidget(0, COL_CANTIDAD)
    precio = form.tabla.cellWidget(0, COL_PRECIO)

    editor = cantidad.lineEdit()
    editor.setFocus()

    qtbot.waitUntil(
        lambda: form.focusWidget() in (cantidad, editor),
    )

    qtbot.keyClick(
        editor,
        Qt.Key.Key_Return,
    )

    qtbot.waitUntil(
        lambda: form.focusWidget() not in (cantidad, editor),
    )

    assert form.focusWidget() in (
        precio,
        precio.lineEdit(),
    )


def test_foco_inicial_va_al_selector_de_proveedor(qtbot):
    from aplicacion.base_datos.registro_modelos import (
        importar_modelos,
    )

    importar_modelos()

    from aplicacion.modulos.compras.documentos_soporte.formulario import (
        FormularioDocumentoSoporte,
    )

    form = FormularioDocumentoSoporte()
    qtbot.addWidget(form)
    form.show()
    qtbot.waitExposed(form)

    qtbot.waitUntil(
        lambda: form.focusWidget() is form.proveedor.btn,
    )
