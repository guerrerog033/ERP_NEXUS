from __future__ import annotations

from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
)

from .column_registry import ColumnRegistry
from .table_definition import TableDefinition

BadgeRole = Qt.UserRole + 50


class RegistrosModel(
    QAbstractTableModel,
):
    """
    Modelo de tabla para QTableView integrado con TableDefinition.
    """

    def __init__(
        self,
        definition: TableDefinition,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.definition = definition

        self._columnas = definition.obtener_columnas()

        self._registros: list[Any] = []

    def rowCount(
        self,
        parent=QModelIndex(),
    ) -> int:

        if parent.isValid():

            return 0

        return len(
            self._registros,
        )

    def columnCount(
        self,
        parent=QModelIndex(),
    ) -> int:

        if parent.isValid():

            return 0

        return len(
            self._columnas,
        )

    def _alineacion_columna(
        self,
        columna,
    ) -> Qt.AlignmentFlag:

        widget = getattr(
            columna,
            "widget",
            "text",
        )

        if widget in {
            "decimal",
            "integer",
        }:

            return (
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter
            )

        alineacion = getattr(
            columna,
            "alineacion",
            "left",
        )

        if alineacion == "right":

            return (
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter
            )

        if alineacion == "center":

            return Qt.AlignmentFlag.AlignCenter

        return (
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

    def _badge_info(
        self,
        valor,
        columna,
    ):

        factory = ColumnRegistry.obtener(
            columna.widget,
        )

        metodo = getattr(
            factory,
            "badge_info",
            None,
        )

        if metodo is None:

            return None

        return metodo(
            valor,
            columna,
        )

    def data(
        self,
        index: QModelIndex,
        role=Qt.DisplayRole,
    ):

        if not index.isValid():

            return None

        columna = self._columnas[
            index.column()
        ]

        registro = self._registros[
            index.row()
        ]

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

        if role == BadgeRole:

            if columna.widget != "status":

                return None

            return self._badge_info(
                valor,
                columna,
            )

        if role == Qt.TextAlignmentRole:

            return int(
                self._alineacion_columna(
                    columna,
                ),
            )

        if role not in (
            Qt.DisplayRole,
            Qt.EditRole,
        ):

            return None

        return ColumnRegistry.formatear_valor(
            columna.widget,
            valor,
            columna,
        )

    def headerData(
        self,
        section: int,
        orientation,
        role=Qt.DisplayRole,
    ):

        if (
            role
            != Qt.DisplayRole
        ):

            return None

        if (
            orientation
            == Qt.Horizontal
            and 0
            <= section
            < len(
                self._columnas,
            )
        ):

            columna = self._columnas[
                section
            ]

            return (
                columna.encabezado
                if columna.visible
                else ""
            )

        return section + 1

    def establecer_registros(
        self,
        registros: list[Any],
    ) -> None:

        self.beginResetModel()

        self._registros = list(
            registros or [],
        )

        self.endResetModel()

    def registro_en_fila(
        self,
        fila: int,
    ) -> Any | None:

        if (
            fila < 0
            or fila
            >= len(
                self._registros,
            )
        ):

            return None

        return self._registros[
            fila
        ]
