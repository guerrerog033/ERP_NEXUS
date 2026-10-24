from .documento_widget import DocumentoWidget


class DocumentoWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        widget = DocumentoWidget()

        if context is not None:

            widget.set_context(
                context
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

        widget.setMaxLength(
            field.longitud_maxima
        )

        if field.placeholder:

            widget.setPlaceholderText(
                field.placeholder
            )

        return widget