"""
Íconos de línea del ERP pintados con un color de la paleta.

Los SVG de ``recursos/iconos`` son de un solo trazo; aquí se tiñen
para que barras de herramientas, menús y botones se vean iguales.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap

from aplicacion.recursos.ui.recursos import Recursos


def pixmap_tenido(
    icono: QIcon,
    tamano: int,
    color: str,
) -> QPixmap:

    base = icono.pixmap(
        QSize(
            tamano,
            tamano,
        ),
    )

    resultado = QPixmap(
        base.size(),
    )

    resultado.setDevicePixelRatio(
        base.devicePixelRatio(),
    )

    resultado.fill(
        Qt.GlobalColor.transparent,
    )

    pintor = QPainter(
        resultado,
    )

    pintor.drawPixmap(
        0,
        0,
        base,
    )

    pintor.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_SourceIn,
    )

    pintor.fillRect(
        resultado.rect(),
        QColor(
            color,
        ),
    )

    pintor.end()

    return resultado


def icono_accion(
    nombre: str,
    color: str = "#334155",
    tamano: int = 20,
) -> QIcon:
    """Ícono de ``iconos/acciones/<nombre>.svg`` teñido."""

    return QIcon(
        pixmap_tenido(
            Recursos.icono(
                f"acciones/{nombre}",
            ),
            tamano,
            color,
        ),
    )


def icono_modulo(
    nombre: str,
    color: str = "#334155",
    tamano: int = 24,
) -> QIcon:
    """Ícono de ``iconos/modulos/<nombre>.svg`` teñido."""

    return QIcon(
        pixmap_tenido(
            Recursos.icono_modulo(
                nombre,
                tamano,
            ),
            tamano,
            color,
        ),
    )
