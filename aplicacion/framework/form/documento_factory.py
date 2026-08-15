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

        widget.setVisible(
            field.visible
        )

        widget.setMaxLength(
            field.longitud_maxima
        )

        if field.placeholder:

            widget.setPlaceholderText(
                field.placeholder
            )

        return widget