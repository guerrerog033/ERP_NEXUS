from PySide6.QtWidgets import QCheckBox


class CheckWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        widget = QCheckBox()

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

        if field.valor_inicial is not None:

            widget.setChecked(
                bool(field.valor_inicial)
            )

        return widget