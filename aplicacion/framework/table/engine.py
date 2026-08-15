from __future__ import annotations

from .binding import TableBinding
from .builder import TableBuilder
from .events import TableEvents
from .table_definition import TableDefinition


class TableEngine:
    """
    Motor principal del Framework de Tablas.

    Coordina:

        • Builder
        • Binding
        • Events

    No conoce:

        • SQLAlchemy
        • CRUD
        • Repositorios
    """

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        definition: TableDefinition,
        *,
        usar_table_view: bool = True,
    ):

        self.definition = definition

        self.usar_table_view = usar_table_view

        self.builder = TableBuilder(
            definition,
            usar_vista=usar_table_view,
        )

        self.events = TableEvents()

        self._widget = None

        self._binding = None

    # =====================================================
    # Construcción
    # =====================================================

    def construir(self):

        if self._widget is None:

            self._widget = self.builder.construir()

            self._binding = TableBinding(

                self.definition,

                self._widget,

                modelo=self.builder.modelo,

            )

        return self._widget

    # =====================================================
    # Widget
    # =====================================================

    @property
    def widget(self):

        return self._widget

    # =====================================================
    # Binding
    # =====================================================

    @property
    def binding(self):

        return self._binding

    # =====================================================
    # Datos
    # =====================================================

    def cargar(
        self,
        registros,
    ):

        self.binding.cargar(
            registros
        )

    def limpiar(self):

        self.binding.limpiar()

    def seleccionado(self):

        return self.binding.seleccionado()

    # =====================================================
    # Eventos
    # =====================================================

    def on(
        self,
        evento,
        callback,
    ):

        self.events.on(
            evento,
            callback,
        )

    def emit(
        self,
        evento,
        *args,
        **kwargs,
    ):

        self.events.emit(
            evento,
            *args,
            **kwargs,
        )