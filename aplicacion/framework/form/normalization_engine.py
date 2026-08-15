from __future__ import annotations

from .form_definition import FormDefinition


class NormalizationEngine:
    """
    Ejecuta los normalizadores definidos
    en los campos de un FormDefinition.

    Responsabilidad única:

        Normalizar un diccionario de datos.

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
    # Normalizar formulario
    # =====================================================

    def normalizar(
        self,
        datos: dict,
    ):

        resultado = {}

        for campo in self.campos:

            resultado[campo.nombre] = self._normalizar_campo(

                campo,

                datos.get(
                    campo.nombre
                ),

            )

        return resultado

    # =====================================================
    # Normalizar un campo
    # =====================================================

    def normalizar_campo(
        self,
        nombre: str,
        valor,
    ):

        campo = self.definition.buscar_campo(
            nombre
        )

        if campo is None:

            return valor

        return self._normalizar_campo(
            campo,
            valor,
        )

    # =====================================================
    # Normalizar campo
    # =====================================================

    def _normalizar_campo(
        self,
        campo,
        valor,
    ):

        for normalizador in campo.normalizers:

            valor = normalizador.normalizar(
                valor
            )

        return valor