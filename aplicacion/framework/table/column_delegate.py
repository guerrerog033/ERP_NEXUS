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

        rect = option.rect.adjusted(
            6,
            6,
            -6,
            -6,
        )

        fondo = QColor(
            badge.get(
                "fondo",
                "#E5E7EB",
            ),
        )

        texto_color = QColor(
            badge.get(
                "texto_color",
                "#111827",
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
            10,
            10,
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
