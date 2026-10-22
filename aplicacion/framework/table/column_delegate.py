from __future__ import annotations

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QStyle,
    QStyleOptionViewItem,
)

from .registros_model import BadgeRole


class ColumnStyledDelegate(
    QStyledItemDelegate,
):
    """
    Delegate de columnas para QTableView.

    Soporta badges de estado y alineación del modelo.
    """

    def initStyleOption(
        self,
        option: QStyleOptionViewItem,
        index,
    ) -> None:

        badge = index.data(
            BadgeRole,
        )

        if isinstance(
            badge,
            dict,
        ):

            option.text = ""

        super().initStyleOption(
            option,
            index,
        )

        alineacion = index.data(
            Qt.TextAlignmentRole,
        )

        if alineacion is not None:

            option.displayAlignment = Qt.Alignment(
                alineacion,
            )

        option.state |= QStyle.StateFlag.State_Active

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index,
    ) -> None:

        badge = index.data(
            BadgeRole,
        )

        if isinstance(
            badge,
            dict,
        ) and badge.get(
            "texto",
        ):

            self._pintar_badge(
                painter,
                option,
                badge,
            )

            return

        super().paint(
            painter,
            option,
            index,
        )

    def _pintar_badge(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        badge: dict,
    ) -> None:

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
        )

        # Etiqueta tipo "píldora" del ancho del texto, alineada a la
        # izquierda. Antes ocupaba toda la celda y la columna de
        # estado se veía como barras de color.
        texto_badge = str(
            badge.get(
                "texto",
                "",
            ),
        )

        metricas = option.fontMetrics

        ancho = min(
            metricas.horizontalAdvance(
                texto_badge,
            )
            + 20,
            option.rect.width() - 12,
        )

        alto = min(
            metricas.height() + 6,
            option.rect.height() - 6,
        )

        rect = option.rect.adjusted(
            8,
            0,
            0,
            0,
        )

        rect.setWidth(
            max(
                ancho,
                0,
            ),
        )

        rect.setTop(
            option.rect.top()
            + (option.rect.height() - alto) // 2,
        )

        rect.setHeight(
            alto,
        )

        fondo = QColor(
            badge.get(
                "fondo",
                "#E2E8F0",
            ),
        )

        texto_color = QColor(
            badge.get(
                "texto_color",
                "#1E293B",
            ),
        )

        painter.setBrush(
            fondo,
        )

        painter.setPen(
            Qt.PenStyle.NoPen,
        )

        painter.drawRoundedRect(
            rect,
            alto / 2,
            alto / 2,
        )

        painter.setPen(
            texto_color,
        )

        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            str(
                badge.get(
                    "texto",
                    "",
                ),
            ),
        )

        painter.restore()
