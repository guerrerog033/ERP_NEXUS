from __future__ import annotations

import pytest

pytestmark = pytest.mark.usefixtures(
    "qapp",
)


def test_boton_buscar_no_es_autodefault():
    """
    El botón de un LookupWidget (cliente/proveedor/producto...) no
    debe poder convertirse en el botón "default" implícito del
    diálogo que lo contenga. Si lo fuera, Enter en cualquier otro
    campo del formulario (fecha, observaciones...) terminaría
    abriendo el buscador en vez de activar la acción esperada —
    reproducido en el formulario de recibo de caja, donde colgaba
    los tests al abrir un QDialog modal sin nadie que lo cierre.
    """

    from unittest.mock import MagicMock

    from aplicacion.framework.lookup.lookup_widget import (
        LookupWidget,
    )

    widget = LookupWidget(
        MagicMock(),
    )

    assert widget.btn.autoDefault() is False
