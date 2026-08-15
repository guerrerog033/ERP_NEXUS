from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class CheckColumnFactory:

    def crear_item(
        self,
        valor,
        columna,
    ) -> QTableWidgetItem:

        item = QTableWidgetItem(
            "Sí"
            if bool(
                valor,
            )
            else "No",
        )

        item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )

        return item

    def formatear_valor(
        self,
        valor,
        columna,
    ) -> str:

        return (
            "Sí"
            if bool(
                valor,
            )
            else "No"
        )
