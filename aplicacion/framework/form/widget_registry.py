from __future__ import annotations

from typing import Any


class WidgetRegistry:
    """
    Registro global de fábricas de widgets.

    Relaciona:

        Field.widget

    con su WidgetFactory correspondiente.
    """

    _factories: dict[str, Any] = {}

    # =====================================================
    # Registrar
    # =====================================================

    @classmethod
    def registrar(
        cls,
        widget: str,
        factory,
    ) -> None:

        if cls.existe(widget):

            raise RuntimeError(
                f"El widget '{widget}' ya está registrado."
            )

        cls._factories[widget] = factory

    # =====================================================
    # Obtener
    # =====================================================

    @classmethod
    def obtener(
        cls,
        widget: str,
    ):

        factory = cls._factories.get(widget)

        if factory is None:

            disponibles = ", ".join(
                cls.widgets()
            )

            raise RuntimeError(

                f"No existe una fábrica registrada para "

                f"'{widget}'. "

                f"Disponibles: {disponibles}"

            )

        return factory

    # =====================================================
    # Existe
    # =====================================================

    @classmethod
    def existe(
        cls,
        widget: str,
    ) -> bool:

        return widget in cls._factories

    # =====================================================
    # Eliminar
    # =====================================================

    @classmethod
    def eliminar(
        cls,
        widget: str,
    ) -> None:

        cls._factories.pop(
            widget,
            None,
        )

    # =====================================================
    # Limpiar
    # =====================================================

    @classmethod
    def limpiar(cls):

        cls._factories.clear()

    # =====================================================
    # Widgets registrados
    # =====================================================

    @classmethod
    def widgets(
        cls,
    ) -> list[str]:

        return sorted(
            cls._factories
        )