from __future__ import annotations

from PySide6.QtWidgets import QHeaderView

from aplicacion.framework.ui.table import Table
from aplicacion.framework.ui.table_view import TableView

from .registros_model import RegistrosModel
from .column_delegate import ColumnStyledDelegate
from .table_definition import TableDefinition


class TableBuilder:
    """
    Construye una tabla Qt a partir de una TableDefinition.
    """

    def __init__(
        self,
        definition: TableDefinition,
        *,
        usar_vista: bool = True,
    ):

        self.definition = definition

        self.usar_vista = usar_vista

        self.widget = None

        self.modelo: RegistrosModel | None = None

    def construir(self):

        if self.widget is not None:

            return self.widget

        if self.usar_vista:

            self.widget = TableView()

            self.modelo = RegistrosModel(
                self.definition,
            )

            self.widget.setModel(
                self.modelo,
            )

            self._configurar_columnas_vista()

            self._configurar_delegates()

        else:

            self.widget = Table()

            self._configurar_columnas()

        self._configurar_header()

        return self.widget

    def _configurar_columnas(self):

        columnas = self.definition.obtener_columnas()

        self.widget.setColumnCount(
            len(columnas),
        )

        self.widget.setHorizontalHeaderLabels(
            self.definition.encabezados(),
        )

        for indice, columna in enumerate(columnas):

            self.widget.setColumnHidden(
                indice,
                not columna.visible,
            )

            if columna.ancho is not None:

                self.widget.setColumnWidth(
                    indice,
                    columna.ancho,
                )

    def _configurar_columnas_vista(self):

        columnas = self.definition.obtener_columnas()

        for indice, columna in enumerate(columnas):

            self.widget.setColumnHidden(
                indice,
                not columna.visible,
            )

            if columna.ancho is not None:

                self.widget.setColumnWidth(
                    indice,
                    columna.ancho,
                )

    def _configurar_header(self):

        columnas = self.definition.obtener_columnas()

        header = self.widget.horizontalHeader()

        for indice, columna in enumerate(columnas):

            if columna.stretch:

                header.setSectionResizeMode(
                    indice,
                    QHeaderView.Stretch,
                )

            else:

                header.setSectionResizeMode(
                    indice,
                    QHeaderView.Interactive,
                )

    def _configurar_delegates(
        self,
    ) -> None:

        if (
            not self.usar_vista
            or self.widget is None
        ):

            return

        delegate = ColumnStyledDelegate(
            self.widget,
        )

        self.widget.setItemDelegate(
            delegate,
        )
