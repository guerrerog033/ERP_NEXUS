from aplicacion.framework.lookup import LookupWidget


class LookupWidgetFactory:

    def crear(
        self,
        field,
        context=None,
    ):

        if field.datasource is None:

            raise RuntimeError(
                "LookupField requiere un datasource."
            )

        datasource = field.datasource()

        widget = LookupWidget(
            datasource,
        )

        if context is not None and hasattr(
            widget,
            "set_context",
        ):

            widget.set_context(
                context
            )

        return widget