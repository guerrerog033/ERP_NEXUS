from __future__ import annotations

from datetime import date, datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class DateColumnFactory:

    def crear_item(
        self,
        valor,
        columna,
    ) -> QTableWidgetItem:

        texto = self._formatear(
            valor,
            getattr(
                columna,
                "formato",
                "%d/%m/%Y",
            ),
        )

        item = QTableWidgetItem(
            texto,
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

        return self._formatear(
            valor,
            getattr(
                columna,
                "formato",
                "%d/%m/%Y",
            ),
        )

    def _formatear(
        self,
        valor,
        formato: str,
    ) -> str:

        if valor is None:

            return ""

        if isinstance(
            valor,
            datetime,
        ):

            valor = valor.date()

        if isinstance(
            valor,
            date,
        ):

            return valor.strftime(
                formato,
            )

        return str(
            valor,
        )
