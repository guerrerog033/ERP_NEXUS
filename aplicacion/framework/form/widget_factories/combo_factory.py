from PySide6.QtWidgets import QComboBox, QSizePolicy


class ComboWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        widget = QComboBox()

        widget.setMinimumHeight(
            36
        )

        widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        widget.setEditable(
            field.editable
        )

        if field.permitir_vacio:

            widget.addItem(
                "",
                None,
            )

        for texto, valor in field.obtener_opciones():

            widget.addItem(
                texto,
                valor,
            )

        widget.setEnabled(
            field.habilitado
        )

        widget.setVisible(
            field.visible
        )

        if field.valor_inicial is not None:

            indice = widget.findData(
                field.valor_inicial
            )

            if indice >= 0:

                widget.setCurrentIndex(
                    indice
                )

        return widget