from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class WidgetAccessor(ABC):
    """
    Clase base para todos los accessors.

    Responsabilidad:

        Widget Qt
            ⇄
        Valor Python
    """

    @abstractmethod
    def leer(
        self,
        widget,
        field,
    ):
        """
        Lee el valor desde el widget.
        """
        raise NotImplementedError

    @abstractmethod
    def escribir(
        self,
        widget,
        valor,
        field,
    ):
        """
        Escribe un valor en el widget.
        """
        raise NotImplementedError