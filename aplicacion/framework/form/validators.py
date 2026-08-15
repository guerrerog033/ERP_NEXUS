from __future__ import annotations

from abc import ABC, abstractmethod


class ValidationError(Exception):
    """Error producido durante una validación."""
    pass


class Validator(ABC):
    """
    Clase base para todos los validadores.
    """

    mensaje = "Valor inválido."

    @abstractmethod
    def validar(self, valor) -> None:
        """
        Lanza ValidationError si el valor no es válido.
        """
        ...


# ==========================================================
# Requerido
# ==========================================================


class Required(Validator):

    mensaje = "Este campo es obligatorio."

    def validar(self, valor):

        if valor is None:
            raise ValidationError(self.mensaje)

        if isinstance(valor, str):

            if valor.strip() == "":
                raise ValidationError(self.mensaje)


# ==========================================================
# Longitud mínima
# ==========================================================


class MinLength(Validator):

    def __init__(self, longitud):

        self.longitud = longitud

    def validar(self, valor):

        if valor is None:
            return

        if len(valor) < self.longitud:

            raise ValidationError(
                f"Debe tener mínimo {self.longitud} caracteres."
            )


# ==========================================================
# Longitud máxima
# ==========================================================


class MaxLength(Validator):

    def __init__(self, longitud):

        self.longitud = longitud

    def validar(self, valor):

        if valor is None:
            return

        if len(valor) > self.longitud:

            raise ValidationError(
                f"Debe tener máximo {self.longitud} caracteres."
            )


# ==========================================================
# Valor mínimo
# ==========================================================


class MinValue(Validator):

    def __init__(self, minimo):

        self.minimo = minimo

    def validar(self, valor):

        if valor is None:
            return

        if valor < self.minimo:

            raise ValidationError(
                f"Debe ser mayor o igual a {self.minimo}."
            )


# ==========================================================
# Valor máximo
# ==========================================================


class MaxValue(Validator):

    def __init__(self, maximo):

        self.maximo = maximo

    def validar(self, valor):

        if valor is None:
            return

        if valor > self.maximo:

            raise ValidationError(
                f"Debe ser menor o igual a {self.maximo}."
            )
        # ==========================================================
# Entero
# ==========================================================

class Integer(Validator):

    mensaje = "Debe ser un número entero."

    def validar(self, valor):

        if valor in (None, ""):
            return

        try:
            int(valor)
        except (TypeError, ValueError):
            raise ValidationError(
                self.mensaje
            )


# ==========================================================
# Decimal
# ==========================================================

class Decimal(Validator):

    mensaje = "Debe ser un número decimal."

    def validar(self, valor):

        if valor in (None, ""):
            return

        try:
            float(valor)
        except (TypeError, ValueError):
            raise ValidationError(
                self.mensaje
            )


# ==========================================================
# Fecha
# ==========================================================

class Date(Validator):

    mensaje = "Fecha inválida."

    def validar(self, valor):

        if valor in (None, ""):
            return

        # La validación específica la realiza
        # el control de fecha.
        pass


# ==========================================================
# Email
# ==========================================================

class Email(Validator):

    mensaje = "Correo electrónico inválido."

    def validar(self, valor):

        if valor in (None, ""):
            return

        if "@" not in valor or "." not in valor:

            raise ValidationError(
                self.mensaje
            )


# ==========================================================
# Teléfono
# ==========================================================

class Phone(Validator):

    mensaje = "Número de teléfono inválido."

    def validar(self, valor):

        if valor in (None, ""):
            return

        permitidos = set(
            "0123456789+-() "
        )

        if any(
            c not in permitidos
            for c in valor
        ):

            raise ValidationError(
                self.mensaje
            )