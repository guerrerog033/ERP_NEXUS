from __future__ import annotations

from aplicacion.framework.form.documento_widget import (
    DocumentoWidget,
)


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

        if field.valor_inicial is not None:

            widget.setText(
                str(field.valor_inicial)
            )

        return widget