from __future__ import annotations

from PySide6.QtCore import QSizeF
from PySide6.QtGui import QPageSize
from PySide6.QtPrintSupport import QPrinter


FORMATOS_PAGINA: dict[
    str,
    dict,
] = {
    "carta": {
        "etiqueta": "Carta",
        "ancho_mm": 215.9,
        "alto_mm": 279.4,
    },
    "media_carta": {
        "etiqueta": "Media carta",
        "ancho_mm": 139.7,
        "alto_mm": 215.9,
    },
    "a4": {
        "etiqueta": "A4",
        "ancho_mm": 210.0,
        "alto_mm": 297.0,
    },
    "tirilla_80": {
        "etiqueta": "Tirilla 80 mm",
        "ancho_mm": 80.0,
        "alto_mm": 297.0,
    },
    "tirilla_58": {
        "etiqueta": "Tirilla 58 mm",
        "ancho_mm": 58.0,
        "alto_mm": 297.0,
    },
}


def aplicar_formato_pagina(
    impresora: QPrinter,
    codigo: str,
) -> None:

    datos = FORMATOS_PAGINA.get(
        codigo,
        FORMATOS_PAGINA["carta"],
    )

    impresora.setPageSize(
        QPageSize(
            QSizeF(
                float(
                    datos["ancho_mm"],
                ),
                float(
                    datos["alto_mm"],
                ),
            ),
            QPageSize.Unit.Millimeter,
        ),
    )
