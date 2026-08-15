from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from aplicacion.framework.base.page import Page
from aplicacion.modulos.logistica.despacho.servicios import (
    ServicioDespacho,
)


class DespachosLogisticaPage(Page):

    titulo = "Despachos logística"

    icono = "logistica"

    def _crear_ui(self) -> None:

        super()._crear_ui()

        layout = self.layout_principal

        layout.addWidget(
            QLabel(
                "Seguimiento de despachos y entregas",
            ),
        )

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(8)

        self.tabla.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows,
        )

        self.tabla.setHorizontalHeaderLabels(
            [
                "Número",
                "Pedido",
                "Remisión",
                "Estado",
                "Ciudad",
                "Transportadora",
                "Conductor",
                "Fecha prog.",
            ],
        )

        layout.addWidget(
            self.tabla,
        )

        barra = QHBoxLayout()

        self.estado = QComboBox()

        for valor in ServicioDespacho.ESTADOS:

            self.estado.addItem(
                valor.replace(
                    "_",
                    " ",
                ).title(),
                valor,
            )

        barra.addWidget(
            QLabel("Estado:"),
        )

        barra.addWidget(
            self.estado,
        )

        btn_cambiar = QPushButton(
            "Cambiar estado",
        )

        btn_cambiar.clicked.connect(
            self._cambiar_estado,
        )

        btn_entregar = QPushButton(
            "Marcar entregado",
        )

        btn_entregar.clicked.connect(
            self._marcar_entregado,
        )

        btn_refrescar = QPushButton(
            "Actualizar",
        )

        btn_refrescar.clicked.connect(
            self._cargar_datos,
        )

        barra.addWidget(
            btn_cambiar,
        )

        barra.addWidget(
            btn_entregar,
        )

        barra.addStretch()

        barra.addWidget(
            btn_refrescar,
        )

        layout.addLayout(
            barra,
        )

        self._cargar_datos()

    def _cargar_datos(self):

        filas = ServicioDespacho.listar()

        self._filas = filas

        self.tabla.setRowCount(
            len(filas),
        )

        for indice, fila in enumerate(
            filas,
        ):

            valores = [
                fila["numero"],
                str(
                    fila.get(
                        "pedido_id",
                        "",
                    )
                    or "",
                ),
                str(
                    fila.get(
                        "remision_numero",
                        "",
                    )
                    or "",
                ),
                fila["estado"],
                fila.get(
                    "ciudad",
                    "",
                )
                or "",
                fila.get(
                    "transportadora",
                    "",
                )
                or "",
                fila.get(
                    "conductor",
                    "",
                )
                or "",
                str(
                    fila.get(
                        "fecha_programada",
                        "",
                    )
                    or "",
                ),
            ]

            for columna, valor in enumerate(
                valores,
            ):

                item = QTableWidgetItem(
                    str(valor),
                )

                if columna == 0:

                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        fila["id"],
                    )

                self.tabla.setItem(
                    indice,
                    columna,
                    item,
                )

        self.tabla.resizeColumnsToContents()

    def _despacho_seleccionado(
        self,
    ) -> dict | None:

        fila = self.tabla.currentRow()

        if fila < 0:

            QMessageBox.warning(
                self,
                "Despachos",
                "Seleccione un despacho.",
            )

            return None

        return self._filas[fila]

    def _cambiar_estado(self):

        registro = self._despacho_seleccionado()

        if registro is None:

            return

        estado = self.estado.currentData()

        try:

            ServicioDespacho.cambiar_estado(
                registro["id"],
                estado,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Despachos",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Despachos",
            f"Estado actualizado a {estado}.",
        )

        self._cargar_datos()

    def _marcar_entregado(self):

        registro = self._despacho_seleccionado()

        if registro is None:

            return

        remision_id = registro.get(
            "remision_id",
        )

        if not remision_id:

            QMessageBox.warning(
                self,
                "Despachos",
                "El despacho no está vinculado "
                "a una remisión interna.",
            )

            return

        try:

            ServicioDespacho.marcar_entregado_por_remision(
                remision_id,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Despachos",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Despachos",
            "Entrega registrada.",
        )

        self._cargar_datos()
