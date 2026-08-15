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

        widget.setVisible(
            field.visible
        )

        if field.valor_inicial is not None:

            widget.setChecked(
                bool(field.valor_inicial)
            )

        return widget