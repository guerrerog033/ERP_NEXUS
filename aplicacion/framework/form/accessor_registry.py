from __future__ import annotations


class AccessorRegistry:
    """
    Registro central de accessors de widgets.

    Relaciona:

        Field.widget

    con el accessor encargado de:

        widget -> valor
        valor  -> widget

    No conoce:

        • Qt
        • SQLAlchemy
        • FormBinding
        • FormEngine
    """

    _accessors: dict[str, object] = {}

    # =====================================================
    # Registrar
    # =====================================================

    @classmethod
    def registrar(
        cls,
        widget: str,
        accessor,
    ) -> None:

        if not widget:
            raise ValueError(
                "El nombre del widget no puede estar vacío."
            )

        if accessor is None:
            raise ValueError(
                f"El accessor para '{widget}' no puede ser None."
            )

        if widget in cls._accessors:

            raise RuntimeError(
                f"Ya existe un accessor para '{widget}'."
            )

        cls._accessors[widget] = accessor

    # =====================================================
    # Obtener
    # =====================================================

    @classmethod
    def obtener(
        cls,
        widget: str,
    ):

        accessor = cls._accessors.get(
            widget
        )

        if accessor is None:

            disponibles = ", ".join(
                sorted(
                    cls._accessors
                )
            )

            raise RuntimeError(
                f"No existe accessor para '{widget}'. "
                f"Disponibles: {disponibles}"
            )

        return accessor

    # =====================================================
    # Existe
    # =====================================================

    @classmethod
    def existe(
        cls,
        widget: str,
    ) -> bool:

        return widget in cls._accessors

    # =====================================================
    # Eliminar
    # =====================================================

    @classmethod
    def eliminar(
        cls,
        widget: str,
    ) -> None:

        cls._accessors.pop(
            widget,
            None,
        )

    # =====================================================
    # Limpiar
    # =====================================================

    @classmethod
    def limpiar(cls) -> None:

        cls._accessors.clear()

    # =====================================================
    # Widgets registrados
    # =====================================================

    @classmethod
    def widgets(
        cls,
    ) -> list[str]:

        return sorted(
            cls._accessors
        )