from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
)


class Tablas:

    @staticmethod
    def configurar(tabla):

        tabla.setAlternatingRowColors(True)

        tabla.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        tabla.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        tabla.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        tabla.setSortingEnabled(True)

        tabla.verticalHeader().setVisible(False)

        tabla.horizontalHeader().setStretchLastSection(True)

        tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

    @staticmethod
    def obtener_id(tabla, columna=0):

        fila = tabla.currentRow()

        if fila < 0:
            return None

        item = tabla.item(fila, columna)

        if item is None:
            return None

        return int(item.text())

    @staticmethod
    def limpiar(tabla):

        tabla.setRowCount(0)

    @staticmethod
    def actualizar_total(label, total):

        if total == 1:

            label.setText("1 registro")

        else:

            label.setText(
                f"{total} registros"
            )