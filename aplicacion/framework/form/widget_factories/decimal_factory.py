from PySide6.QtWidgets import QDoubleSpinBox


class DecimalWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        widget = QDoubleSpinBox()

        widget.setMinimumHeight(
            30
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

        if hasattr(
            field,
            "decimales",
        ):

            widget.setDecimals(
                field.decimales
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
                float(field.valor_inicial)
            )

        return widget