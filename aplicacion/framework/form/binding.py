from __future__ import annotations

from .accessor_registry import AccessorRegistry
from .form_definition import FormDefinition


class FormBinding:
    """
    Sincroniza objetos de dominio y widgets.

    Responsabilidad única:

        Objeto  <------>  Widgets

    No conoce:

        - Qt
        - SQLAlchemy
        - Validaciones
        - Normalizadores
        - CRUD
    """

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        definition: type[FormDefinition],
        widgets: dict,
    ):

        self.definition = definition

        self.widgets = widgets

    # =====================================================
    # Cargar objeto
    # =====================================================

    def cargar(
        self,
        objeto,
    ):

        if objeto is None:

            return

        for campo in self.definition.obtener_campos():

            widget = self.widgets.get(
                campo.nombre
            )

            if widget is None:

                continue

            if not hasattr(
                objeto,
                campo.nombre,
            ):

                continue

            accessor = AccessorRegistry.obtener(
                campo.widget
            )

            accessor.escribir(
                widget,
                getattr(
                    objeto,
                    campo.nombre,
                ),
                campo,
            )

    # =====================================================
    # Obtener valores
    # =====================================================

    def valores(
        self,
    ):

        datos = {}

        for campo in self.definition.obtener_campos():

            widget = self.widgets.get(
                campo.nombre
            )

            if widget is None:

                continue

            accessor = AccessorRegistry.obtener(
                campo.widget
            )

            datos[
                campo.nombre
            ] = accessor.leer(
                widget,
                campo,
            )

        return datos

    # =====================================================
    # Obtener valor
    # =====================================================

    def valor(
        self,
        nombre: str,
    ):

        campo = self.definition.buscar_campo(
            nombre
        )

        if campo is None:

            return None

        widget = self.widgets.get(
            nombre
        )

        if widget is None:

            return None

        accessor = AccessorRegistry.obtener(
            campo.widget
        )

        return accessor.leer(
            widget,
            campo,
        )

    # =====================================================
    # Establecer valor
    # =====================================================

    def set_valor(
        self,
        nombre: str,
        valor,
    ):

        campo = self.definition.buscar_campo(
            nombre
        )

        if campo is None:

            return

        widget = self.widgets.get(
            nombre
        )

        if widget is None:

            return

        accessor = AccessorRegistry.obtener(
            campo.widget
        )

        accessor.escribir(
            widget,
            valor,
            campo,
        )

    # =====================================================
    # Actualizar objeto
    # =====================================================

    def actualizar(
        self,
        objeto,
        datos,
    ):

        if objeto is None:

            return None

        for nombre, valor in datos.items():

            if not hasattr(
                objeto,
                nombre,
            ):

                continue

            setattr(
                objeto,
                nombre,
                valor,
            )

        return objeto

    # =====================================================
    # Limpiar formulario
    # =====================================================

    def limpiar(
        self,
    ):

        for campo in self.definition.obtener_campos():

            widget = self.widgets.get(
                campo.nombre
            )

            if widget is None:

                continue

            accessor = AccessorRegistry.obtener(
                campo.widget
            )

            accessor.escribir(
                widget,
                campo.valor_inicial,
                campo,
            )