from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QScrollArea,
    QVBoxLayout,
)

from aplicacion.modulos.ventas.facturas.formulario import (
    FormularioFacturaVenta,
)


def mostrar_formulario_factura(
    id_registro: int,
    *,
    parent=None,
    titulo: str = "Factura de venta",
) -> None:

    ventana = QDialog(
        parent,
    )

    ventana.setWindowTitle(
        titulo,
    )

    ventana.setModal(
        True,
    )

    formulario = FormularioFacturaVenta(
        id_registro=id_registro,
        parent=ventana,
    )

    margen = 32

    ancho_padre = (
        parent.width()
        if parent is not None
        else 1200
    )

    alto_padre = (
        parent.height()
        if parent is not None
        else 800
    )

    ancho = min(
        formulario.ancho,
        max(
            900,
            ancho_padre - margen,
        ),
    )

    alto = min(
        formulario.alto,
        max(
            620,
            alto_padre - margen,
        ),
    )

    ventana.resize(
        ancho,
        alto,
    )

    ventana.setMinimumSize(
        min(
            ancho,
            900,
        ),
        min(
            alto,
            620,
        ),
    )

    layout = QVBoxLayout(
        ventana,
    )

    layout.setContentsMargins(
        6,
        6,
        6,
        6,
    )

    scroll = QScrollArea()

    scroll.setWidgetResizable(
        True,
    )

    scroll.setFrameShape(
        QFrame.Shape.NoFrame,
    )

    scroll.setHorizontalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAsNeeded,
    )

    scroll.setVerticalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAsNeeded,
    )

    scroll.setWidget(
        formulario,
    )

    layout.addWidget(
        scroll,
    )

    ventana.exec()
