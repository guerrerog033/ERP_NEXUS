from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QLabel,
    QTableWidgetItem,
)

from aplicacion.framework.lookup import LookupWidget
from aplicacion.framework.ui.inquiry_page import InquiryPage
from aplicacion.maestros.terceros.cliente_lookup import (
    ClienteLookup,
)
from aplicacion.modulos.cartera.servicios import (
    ServicioCartera,
)


class CarteraCxCPage(InquiryPage):

    titulo = "Cuentas por cobrar"

    _NOMBRE_EXPORT = "cartera_cxc"

    _COLUMNAS = [
        "Número",
        "Cliente",
        "Fecha",
        "Vencimiento",
        "Total",
        "Pagado",
        "Saldo",
        "Estado",
        "Días mora",
    ]

    def _crear_filtros(self) -> None:

        self._layout_filtros.addWidget(
            QLabel("Cliente:"),
        )

        self.cliente = LookupWidget(
            ClienteLookup(),
            self,
        )

        self._layout_filtros.addWidget(
            self.cliente,
            1,
        )

        self.solo_vencidos = QCheckBox(
            "Solo vencidos",
        )

        self._layout_filtros.addWidget(
            self.solo_vencidos,
        )

    def _consultar(self) -> None:

        filas = ServicioCartera.listar_cxc(
            tercero_id=self.cliente.valor(),
            solo_vencidos=self.solo_vencidos.isChecked(),
        )

        self._mostrar_filas(filas)

    def _mostrar_filas(
        self,
        filas: list[dict],
    ) -> None:

        self.tabla.setRowCount(
            len(filas),
        )

        for i, fila in enumerate(filas):

            valores = [
                fila["numero"],
                fila["tercero"],
                str(fila["fecha"]),
                str(
                    fila["fecha_vencimiento"]
                    or "",
                ),
                f"{fila['total']:,.2f}",
                f"{fila['valor_pagado']:,.2f}",
                f"{fila['saldo']:,.2f}",
                fila["estado_pago"],
                str(fila["dias_mora"]),
            ]

            for j, valor in enumerate(
                valores,
            ):

                item = QTableWidgetItem(
                    valor,
                )

                if (
                    fila["dias_mora"] > 0
                    and j == 8
                ):

                    item.setForeground(
                        Qt.red,
                    )

                self.tabla.setItem(
                    i,
                    j,
                    item,
                )

        self.tabla.resizeColumnsToContents()
