from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem

from aplicacion.framework.utilidades.moneda import (
    formatear_decimal,
)


class DecimalColumnFactory:

    def crear_item(
        self,
        valor,
        columna,
    ) -> QTableWidgetItem:

        texto = formatear_decimal(
            valor,
            decimales=getattr(
                columna,
                "decimales",
                2,
            ),
            prefijo=getattr(
                columna,
                "prefijo",
                "",
            )
            or columna.meta(
                "prefijo",
                "",
            ),
            sufijo=getattr(
                columna,
                "sufijo",
                "",
            )
            or columna.meta(
                "sufijo",
                "",
            ),
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

        return formatear_decimal(
            valor,
            decimales=getattr(
                columna,
                "decimales",
                2,
            ),
            prefijo=getattr(
                columna,
                "prefijo",
                "",
            )
            or columna.meta(
                "prefijo",
                "",
            ),
            sufijo=getattr(
                columna,
                "sufijo",
                "",
            )
            or columna.meta(
                "sufijo",
                "",
            ),
        )
