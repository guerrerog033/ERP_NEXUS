from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
)


def llenar_tabla_reporte(
    tabla: QTableWidget,
    columnas: list[str],
    filas: list[dict],
    *,
    campos: list[str] | None = None,
    columnas_numericas: set[int] | None = None,
    formateadores: dict[
        int,
        Callable[[object], str],
    ] | None = None,
) -> None:

    campos = campos or columnas
    columnas_numericas = columnas_numericas or set()
    formateadores = formateadores or {}

    tabla.setColumnCount(
        len(columnas),
    )

    tabla.setHorizontalHeaderLabels(
        columnas,
    )

    tabla.setRowCount(
        len(filas),
    )

    for indice_fila, fila in enumerate(
        filas,
    ):

        for indice_columna, campo in enumerate(
            campos,
        ):

            valor = fila.get(
                campo,
                "",
            )

            if indice_columna in formateadores:

                texto = formateadores[
                    indice_columna
                ](
                    valor,
                )

            elif isinstance(
                valor,
                float,
            ):

                texto = f"{valor:,.2f}"

            else:

                texto = str(
                    valor or "",
                )

            item = QTableWidgetItem(
                texto,
            )

            if (
                indice_columna
                in columnas_numericas
            ):

                item.setTextAlignment(
                    Qt.AlignRight
                    | Qt.AlignVCenter,
                )

            tabla.setItem(
                indice_fila,
                indice_columna,
                item,
            )

    tabla.resizeColumnsToContents()
