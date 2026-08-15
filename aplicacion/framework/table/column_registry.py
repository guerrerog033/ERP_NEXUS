from __future__ import annotations


class ColumnRegistry:
    """
    Registro central de factories de columnas de tabla.

    Relaciona ``Column.widget`` con el factory que formatea
    valores para ``QTableWidgetItem``.
    """

    _factories: dict[str, object] = {}

    @classmethod
    def registrar(
        cls,
        widget: str,
        factory,
    ) -> None:

        if not widget:

            raise ValueError(
                "El nombre del widget no puede estar vacío.",
            )

        if factory is None:

            raise ValueError(
                f"El factory para '{widget}' no puede ser None.",
            )

        cls._factories[widget] = factory

    @classmethod
    def obtener(
        cls,
        widget: str,
    ):

        factory = cls._factories.get(
            widget,
        )

        if factory is None:

            factory = cls._factories.get(
                "text",
            )

        if factory is None:

            raise RuntimeError(
                "No hay factory de columna 'text' registrado.",
            )

        return factory

    @classmethod
    def formatear_valor(
        cls,
        widget: str,
        valor,
        columna,
    ) -> str:

        factory = cls.obtener(
            widget,
        )

        metodo = getattr(
            factory,
            "formatear_valor",
            None,
        )

        if metodo is not None:

            return metodo(
                valor,
                columna,
            )

        if valor is None:

            return ""

        return str(
            valor,
        )

    @classmethod
    def limpiar(cls) -> None:

        cls._factories.clear()
