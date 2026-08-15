from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class IntegerColumnFactory:

    def crear_item(
        self,
        valor,
        columna,
    ) -> QTableWidgetItem:

        if valor is None:

            texto = ""

        else:

            try:

                texto = f"{int(valor):,}".replace(
                    ",",
                    ".",
                )

            except (
                TypeError,
                ValueError,
            ):

                texto = str(
                    valor,
                )

        item = QTableWidgetItem(
            texto,
        )

        item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter,
        )

        return item

    def formatear_valor(
        self,
        valor,
        columna,
    ) -> str:

        if valor is None:

            return ""

        try:

            return f"{int(valor):,}".replace(
                ",",
                ".",
            )

        except (
            TypeError,
            ValueError,
        ):

            return str(
                valor,
            )
