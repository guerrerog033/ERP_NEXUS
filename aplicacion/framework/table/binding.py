from __future__ import annotations

from PySide6.QtWidgets import QTableWidgetItem

from aplicacion.framework.ui.table import Table

from .column_registry import ColumnRegistry
from .registros_model import RegistrosModel
from .table_definition import TableDefinition

import aplicacion.framework.table.column_factories  # noqa: F401


class TableBinding:
    """
    Sincroniza una colección de objetos con una tabla.
    """

    def __init__(
        self,
        definition: TableDefinition,
        widget,
        *,
        modelo: RegistrosModel | None = None,
    ):

        self.definition = definition

        self.widget = widget

        self.modelo = modelo

        self.registros = []

    def cargar(
        self,
        registros,
    ):

        self.registros = list(registros)

        if self.modelo is not None:

            self.modelo.establecer_registros(
                self.registros,
            )

            self.widget.resizeColumnsToContents()

            return

        columnas = self.definition.obtener_columnas()

        self.widget.setSortingEnabled(False)

        self.widget.clearContents()

        self.widget.setRowCount(
            len(self.registros),
        )

        for fila, registro in enumerate(self.registros):

            for indice, columna in enumerate(columnas):

                item = self._crear_item(
                    registro,
                    columna,
                )

                self.widget.setItem(
                    fila,
                    indice,
                    item,
                )

        self.widget.setSortingEnabled(True)

        self.widget.resizeColumnsToContents()

    def limpiar(self):

        self.registros.clear()

        if self.modelo is not None:

            self.modelo.establecer_registros([])

            return

        self.widget.clearContents()

        self.widget.setRowCount(0)

    def seleccionado(self):

        if self.modelo is not None:

            indice = self.widget.currentIndex()

            if not indice.isValid():

                return None

            return self.modelo.registro_en_fila(
                indice.row(),
            )

        fila = self.widget.currentRow()

        if fila < 0:

            return None

        if fila >= len(self.registros):

            return None

        return self.registros[fila]

    def registros_cargados(self):

        return list(
            self.registros,
        )

    def _crear_item(
        self,
        registro,
        columna,
    ):

        if isinstance(
            registro,
            dict,
        ):

            valor = registro.get(
                columna.nombre,
            )

        else:

            valor = getattr(
                registro,
                columna.nombre,
                None,
            )

        factory = ColumnRegistry.obtener(
            columna.widget,
        )

        return factory.crear_item(
            valor,
            columna,
        )
