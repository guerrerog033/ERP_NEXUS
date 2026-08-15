from __future__ import annotations

from abc import ABC, abstractmethod

from .result import DataResult


class DataSource(ABC):
    """
    Contrato base para cualquier origen de datos.

    Un DataSource puede obtener información desde:

        • SQLAlchemy
        • API REST
        • Memoria
        • CSV
        • Excel
        • etc.
    """

    # ==================================================
    # Listar
    # ==================================================

    @abstractmethod
    def listar(
        self,
        **kwargs,
    ) -> DataResult:
        ...

    # ==================================================
    # Buscar
    # ==================================================

    @abstractmethod
    def buscar(
        self,
        texto: str,
    ) -> DataResult:
        ...

    # ==================================================
    # Obtener
    # ==================================================

    @abstractmethod
    def obtener(
        self,
        id_registro,
    ):
        ...

    # ==================================================
    # Guardar
    # ==================================================

    @abstractmethod
    def guardar(
        self,
        datos,
        id_registro=None,
    ):
        ...

    # ==================================================
    # Eliminar
    # ==================================================

    @abstractmethod
    def eliminar(
        self,
        id_registro,
    ):
        ...