from PySide6.QtWidgets import QLineEdit


class PasswordWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        widget = QLineEdit()

        widget.setEchoMode(
            QLineEdit.Password
        )

        widget.setMinimumHeight(
            36
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

        if field.longitud_maxima is not None:

            widget.setMaxLength(
                field.longitud_maxima
            )

        return widget