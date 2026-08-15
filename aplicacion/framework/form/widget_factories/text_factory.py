from PySide6.QtWidgets import QLineEdit, QSizePolicy


class TextWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        widget = QLineEdit()

        widget.setMinimumHeight(
            36
        )

        widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
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

        if field.placeholder:

            widget.setPlaceholderText(
                field.placeholder
            )

        return widget