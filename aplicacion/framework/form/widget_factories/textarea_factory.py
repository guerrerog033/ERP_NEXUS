from PySide6.QtWidgets import QTextEdit


class TextAreaWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        widget = QTextEdit()

        widget.setMinimumHeight(
            field.alto
        )

        widget.setEnabled(
            field.habilitado
        )

        widget.setVisible(
            field.visible
        )

        if field.placeholder:

            widget.setPlaceholderText(
                field.placeholder
            )

        return widget