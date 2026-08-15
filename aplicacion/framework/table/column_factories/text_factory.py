from __future__ import annotations

from datetime import date, datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class TextColumnFactory:

    def crear_item(
        self,
        valor,
        columna,
    ) -> QTableWidgetItem:

        item = QTableWidgetItem(
            ""
            if valor is None
            else str(
                valor,
            ),
        )

        self._alinear(
            item,
            columna,
        )

        return item

    def formatear_valor(
        self,
        valor,
        columna,
    ) -> str:

        if valor is None:

            return ""

        return str(
            valor,
        )

    def _alinear(
        self,
        item: QTableWidgetItem,
        columna,
    ) -> None:

        alineacion = getattr(
            columna,
            "alineacion",
            "left",
        )

        if alineacion == "right":

            item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter,
            )

        elif alineacion == "center":

            item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter,
            )
