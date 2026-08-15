from PySide6.QtWidgets import QSpinBox


class IntegerWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        widget = QSpinBox()

        widget.setMinimumHeight(
            36
        )

        widget.setEnabled(
            field.habilitado
        )

        widget.setVisible(
            field.visible
        )

        if hasattr(
            field,
            "minimo",
        ) and field.minimo is not None:

            widget.setMinimum(
                field.minimo
            )

        if hasattr(
            field,
            "maximo",
        ) and field.maximo is not None:

            widget.setMaximum(
                field.maximo
            )

        if field.valor_inicial is not None:

            widget.setValue(
                int(field.valor_inicial)
            )

        return widget