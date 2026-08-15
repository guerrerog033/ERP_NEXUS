from __future__ import annotations

from .form_definition import FormDefinition
from .validators import ValidationError


class ValidationEngine:
    """
    Ejecuta los validadores definidos
    en los campos de un FormDefinition.

    Responsabilidad única:

        Validar un diccionario de datos.

    No conoce:

        - Qt
        - Widgets
        - SQLAlchemy
        - CRUD
    """

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        definition: type[FormDefinition],
    ):

        self.definition = definition

        self.campos = definition.obtener_campos()

    # =====================================================
    # Validar formulario
    # =====================================================

    def errores(
        self,
        datos: dict,
    ) -> dict:

        resultado = {}

        for campo in self.campos:

            error = self._validar_campo(
                campo,
                datos.get(
                    campo.nombre,
                ),
            )

            if error is not None:

                resultado[
                    campo.nombre
                ] = error

        return resultado

    def validar(
        self,
        datos: dict,
    ):

        errores = self.errores(
            datos,
        )

        if errores:

            raise ValidationError(
                "\n".join(
                    str(error)
                    for error in errores.values()
                )
            )

        return datos

    # =====================================================
    # Validar un campo
    # =====================================================

    def validar_campo(
        self,
        nombre: str,
        valor,
    ):

        campo = self.definition.buscar_campo(
            nombre
        )

        if campo is None:

            return valor

        error = self._validar_campo(
            campo,
            valor,
        )

        if error is not None:

            raise ValidationError(
                str(error)
            )

        return valor

    # =====================================================
    # Validar campo
    # =====================================================

    def _validar_campo(
        self,
        campo,
        valor,
    ):

        for validador in campo.validadores:

            try:

                validador.validar(
                    valor
                )

            except ValidationError as error:

                return error

        return None