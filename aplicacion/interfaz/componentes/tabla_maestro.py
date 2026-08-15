from PySide6.QtWidgets import (
    QTableWidget,
    QAbstractItemView,
    QHeaderView,
)


class TablaMaestro(QTableWidget):

    def __init__(self):

        super().__init__()

        # Seleccionar filas completas
        self.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        # Solo una fila a la vez
        self.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        # No editar directamente
        self.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        # Alternar colores
        self.setAlternatingRowColors(True)

        # Selección por fila
        self.setSortingEnabled(True)

        # Última columna ocupa el espacio restante
        self.horizontalHeader().setStretchLastSection(True)

        # Redimensionar automáticamente
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        # Ocultar numeración lateral
        self.verticalHeader().setVisible(False)