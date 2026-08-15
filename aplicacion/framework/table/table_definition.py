from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

from .column import Column


@dataclass(slots=True)
class TableDefinition:
    """
    Describe la estructura lógica de una tabla.

    Es completamente declarativa.

    No conoce:

        • Qt
        • SQLAlchemy
        • DataGrid
        • CRUD

    Solo describe las columnas.
    """

    titulo: str = ""

    columnas: list[Column] = field(
        default_factory=list
    )

    filtros: list = field(
        default_factory=list,
    )

    # =====================================================
    # Obtener columnas
    # =====================================================

    def obtener_columnas(
        self,
    ) -> list[Column]:

        return list(
            self.columnas
        )

    # =====================================================
    # Obtener columnas visibles
    # =====================================================

    def obtener_visibles(
        self,
    ) -> list[Column]:

        return [

            columna

            for columna in self.columnas

            if columna.visible

        ]

    # =====================================================
    # Buscar columna
    # =====================================================

    def columna(
        self,
        nombre: str,
    ) -> Column | None:

        for columna in self.columnas:

            if columna.nombre == nombre:

                return columna

        return None

    # =====================================================
    # Nombres
    # =====================================================

    def nombres(
        self,
    ) -> list[str]:

        return [

            columna.nombre

            for columna in self.columnas

        ]

    # =====================================================
    # Encabezados
    # =====================================================

    def encabezados(
        self,
    ) -> list[str]:

        return [

            columna.encabezado
            if columna.visible
            else ""

            for columna in self.columnas

        ]

    # =====================================================
    # Cantidad
    # =====================================================

    def __len__(self):

        return len(
            self.columnas
        )

    # =====================================================
    # Iterador
    # =====================================================

    def __iter__(self) -> Iterator[Column]:

        return iter(
            self.columnas
        )