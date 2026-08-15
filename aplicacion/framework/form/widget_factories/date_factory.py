from PySide6.QtCore import QDate

from PySide6.QtWidgets import QDateEdit


class DateWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        widget = QDateEdit()

        widget.setCalendarPopup(
            True
        )

        widget.setMinimumHeight(
            36
        )

        widget.setEnabled(
            field.habilitado
        )

        widget.setVisible(
            field.visible
        )

        if field.valor_inicial is not None:

            if isinstance(
                field.valor_inicial,
                QDate,
            ):

                widget.setDate(
                    field.valor_inicial
                )

            else:

                widget.setDate(
                    QDate.fromString(
                        str(field.valor_inicial),
                        "yyyy-MM-dd",
                    )
                )

        return widget