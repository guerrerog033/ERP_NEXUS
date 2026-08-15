from __future__ import annotations

from PySide6.QtWidgets import QTableWidgetItem

from .text_factory import TextColumnFactory


class LookupColumnFactory(
    TextColumnFactory,
):

    def crear_item(
        self,
        valor,
        columna,
    ) -> QTableWidgetItem:

        if valor is None:

            return super().crear_item(
                "",
                columna,
            )

        if hasattr(
            valor,
            "__str__",
        ) and not isinstance(
            valor,
            (
                str,
                int,
                float,
            ),
        ):

            for atributo in (
                "nombre",
                "razon_social",
                "descripcion",
                "codigo",
            ):

                texto = getattr(
                    valor,
                    atributo,
                    None,
                )

                if texto:

                    return super().crear_item(
                        texto,
                        columna,
                    )

        return super().crear_item(
            valor,
            columna,
        )
