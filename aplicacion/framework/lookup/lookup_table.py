from __future__ import annotations

from PySide6.QtWidgets import (
    QTableWidget,
    QAbstractItemView,
    QTableWidgetItem,
    QHeaderView,
)


class LookupTable(QTableWidget):

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(parent)

        self.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.setAlternatingRowColors(
            True
        )

        self.verticalHeader().hide()

        self.setSortingEnabled(
            True
        )

        self.horizontalHeader().setStretchLastSection(
            True
        )

        self.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.Stretch,
        )


    # =====================================================
    # Limpiar
    # =====================================================

    def limpiar(self):

        self.setSortingEnabled(False)

        self.clear()

        self.setRowCount(0)

        self.setColumnCount(0)


    # =====================================================
    # Cargar resultados
    # =====================================================

    def cargar(
        self,
        resultados,
    ):

        self.limpiar()

        self.setColumnCount(2)

        self.setHorizontalHeaderLabels(
            [
                "Código",
                "Descripción",
            ]
        )

        self.setRowCount(
            len(resultados)
        )

        for fila, resultado in enumerate(resultados):

            item_codigo = QTableWidgetItem(
                resultado.codigo
            )

            item_descripcion = QTableWidgetItem(
                resultado.texto
            )

            #
            # Guardamos el LookupResult completo
            #

            item_codigo.setData(
                1000,
                resultado,
            )

            self.setItem(
                fila,
                0,
                item_codigo,
            )

            self.setItem(
                fila,
                1,
                item_descripcion,
            )

        self.resizeColumnsToContents()

        self.setSortingEnabled(True)


    # =====================================================
    # Resultado seleccionado
    # =====================================================

    def resultado_seleccionado(self):

        fila = self.currentRow()

        if fila < 0:

            return None

        item = self.item(
            fila,
            0,
        )

        if item is None:

            return None

        return item.data(1000)