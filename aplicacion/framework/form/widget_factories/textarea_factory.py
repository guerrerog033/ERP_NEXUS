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

        # setVisible(True) sobre un widget sin padre lo muestra como
        # ventana suelta (parpadeo al abrir formularios). Solo se
        # oculta cuando corresponde; al agregarlo al formulario se ve.
        if not field.visible:

            widget.setVisible(
                False,
            )

        if field.placeholder:

            widget.setPlaceholderText(
                field.placeholder
            )

        return widget