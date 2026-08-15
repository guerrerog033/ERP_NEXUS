from __future__ import annotations

from abc import ABC, abstractmethod


class Normalizer(ABC):
    """
    Clase base para todos los normalizadores.

    Transforman el valor antes de validarlo
    y antes de enviarlo al servicio.
    """

    @abstractmethod
    def normalizar(self, valor):
        ...



# ==========================================================
# Trim
# ==========================================================

class Trim(Normalizer):

    def normalizar(self, valor):

        if isinstance(valor, str):

            return valor.strip()

        return valor



# ==========================================================
# Upper
# ==========================================================

class Upper(Normalizer):

    def normalizar(self, valor):

        if isinstance(valor, str):

            return valor.upper()

        return valor



# ==========================================================
# Lower
# ==========================================================

class Lower(Normalizer):

    def normalizar(self, valor):

        if isinstance(valor, str):

            return valor.lower()

        return valor



# ==========================================================
# Title
# ==========================================================

class Title(Normalizer):

    def normalizar(self, valor):

        if isinstance(valor, str):

            return valor.title()

        return valor



# ==========================================================
# Capitalize
# ==========================================================

class Capitalize(Normalizer):

    def normalizar(self, valor):

        if isinstance(valor, str):

            return valor.capitalize()

        return valor



# ==========================================================
# RemoveMultipleSpaces
# ==========================================================

class RemoveMultipleSpaces(Normalizer):

    def normalizar(self, valor):

        if not isinstance(valor, str):

            return valor

        return " ".join(
            valor.split()
        )