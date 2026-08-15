from PySide6.QtWidgets import QLineEdit


class PhoneWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        widget = QLineEdit()

        widget.setMinimumHeight(
            36
        )

        widget.setEnabled(
            field.habilitado
        )

        widget.setVisible(
            field.visible
        )

        if field.longitud_maxima is not None:

            widget.setMaxLength(
                field.longitud_maxima
            )

        return widget