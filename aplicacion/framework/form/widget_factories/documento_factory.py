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

        # setVisible(True) sobre un widget sin padre lo muestra como
        # ventana suelta (parpadeo al abrir formularios). Solo se
        # oculta cuando corresponde; al agregarlo al formulario se ve.
        if not field.visible:

            widget.setVisible(
                False,
            )

        if field.valor_inicial is not None:

            widget.setText(
                str(field.valor_inicial)
            )

        return widget