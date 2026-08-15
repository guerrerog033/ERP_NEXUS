from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)

from aplicacion.framework.base.page import Page

from aplicacion.modulos.compras.ordenes.servicios import (
    ServicioOrdenCompra,
)
from aplicacion.modulos.inventario.bodegas.servicios import (
    ServicioBodega,
)


class RecepcionesCompraPage(Page):

    titulo = "Recepciones de compra"

    def _crear_ui(self) -> None:

        super()._crear_ui()

        self._pendientes: dict[
            int,
            list[dict],
        ] = {}

        self._construir()

        self._cargar_ordenes()

    def _construir(self):

        layout = self.layout_principal

        form = QFormLayout()

        self.orden = QComboBox()

        self.orden.currentIndexChanged.connect(
            self._cargar_lineas,
        )

        form.addRow(
            "Orden de compra:",
            self.orden,
        )

        self.bodega = QComboBox()

        for bodega in ServicioBodega.listar_activas():

            self.bodega.addItem(
                f"{bodega.codigo} - {bodega.nombre}",
                bodega.id,
            )

        form.addRow(
            "Bodega:",
            self.bodega,
        )

        self.fecha = QDateEdit()

        self.fecha.setCalendarPopup(
            True,
        )

        self.fecha.setDate(
            QDate.currentDate(),
        )

        form.addRow(
            "Fecha:",
            self.fecha,
        )

        self.observaciones = QLineEdit()

        form.addRow(
            "Observaciones:",
            self.observaciones,
        )

        layout.addLayout(form)

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(5)

        self.tabla.setHorizontalHeaderLabels(
            [
                "Producto",
                "Pedido",
                "Recibido",
                "Pendiente",
                "Recibir",
            ],
        )

        layout.addWidget(self.tabla)

        barra = QHBoxLayout()

        btn = QPushButton(
            "Registrar recepción",
        )

        btn.clicked.connect(
            self._guardar,
        )

        barra.addWidget(btn)
        barra.addStretch()

        layout.addLayout(barra)

        layout.addWidget(
            QLabel(
                "Historial de recepciones",
            ),
        )

        self.historial = QTableWidget()

        self.historial.setColumnCount(6)

        self.historial.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows,
        )

        self.historial.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection,
        )

        self.historial.setHorizontalHeaderLabels(
            [
                "Número",
                "Fecha",
                "Orden",
                "Cantidad",
                "Estado",
                "Observaciones",
            ],
        )

        layout.addWidget(
            self.historial,
        )

        barra_historial = QHBoxLayout()

        self.btn_anular = QPushButton(
            "Anular recepción",
        )

        self.btn_anular.clicked.connect(
            self._anular_recepcion,
        )

        barra_historial.addWidget(
            self.btn_anular,
        )

        barra_historial.addStretch()

        layout.addLayout(
            barra_historial,
        )

        self._cargar_historial()

    def _cargar_historial(self):

        filas = ServicioOrdenCompra.listar_recepciones()

        self._historial_filas = filas

        self.historial.setRowCount(
            len(filas),
        )

        for indice, fila in enumerate(filas):

            estado = (
                "Activa"
                if fila.get("activo", True)
                else "Anulada"
            )

            valores = [
                fila["numero"],
                str(fila["fecha"]),
                fila["orden_numero"],
                f"{fila['cantidad_total']:,.2f}",
                estado,
                fila["observaciones"],
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

                if not fila.get("activo", True):

                    item.setForeground(
                        Qt.GlobalColor.gray,
                    )

                self.historial.setItem(
                    indice,
                    columna,
                    item,
                )

        self.historial.resizeColumnsToContents()

    def _anular_recepcion(self):

        fila = self.historial.currentRow()

        if fila < 0:

            QMessageBox.warning(
                self,
                "Anular recepción",
                "Seleccione una recepción del historial.",
            )

            return

        item = self.historial.item(
            fila,
            0,
        )

        recepcion_id = (
            item.data(
                Qt.ItemDataRole.UserRole,
            )
            if item
            else None
        )

        if recepcion_id is None:

            return

        registro = self._historial_filas[fila]

        if not registro.get("activo", True):

            QMessageBox.warning(
                self,
                "Anular recepción",
                "La recepción ya está anulada.",
            )

            return

        motivo, ok = QInputDialog.getText(
            self,
            "Anular recepción",
            "Motivo de anulación (opcional):",
        )

        if not ok:

            return

        confirmar = QMessageBox.question(
            self,
            "Anular recepción",
            (
                f"¿Anular la recepción {registro['numero']}? "
                "Se revertirá el inventario y las cantidades "
                "recibidas en la orden de compra."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if (
            confirmar
            != QMessageBox.StandardButton.Yes
        ):

            return

        try:

            ServicioOrdenCompra.anular_recepcion(
                recepcion_id,
                motivo=motivo,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Anular recepción",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Anular recepción",
            f"Recepción {registro['numero']} anulada.",
        )

        self._cargar_ordenes()
        self._cargar_historial()

    def _cargar_ordenes(self):

        self.orden.blockSignals(
            True,
        )

        self.orden.clear()

        self._pendientes.clear()

        ordenes = (
            ServicioOrdenCompra
            .listar_pendientes_recepcion()
        )

        for orden in ordenes:

            lineas = []

            for detalle in orden.detalles:

                pendiente = float(
                    detalle.cantidad or 0,
                ) - float(
                    detalle.cantidad_recibida
                    or 0,
                )

                if pendiente <= 0:

                    continue

                lineas.append(
                    {
                        "orden_detalle_id": detalle.id,
                        "descripcion": detalle.descripcion,
                        "cantidad": float(
                            detalle.cantidad or 0,
                        ),
                        "recibida": float(
                            detalle.cantidad_recibida
                            or 0,
                        ),
                        "pendiente": pendiente,
                    },
                )

            if not lineas:

                continue

            self._pendientes[
                orden.id
            ] = lineas

            self.orden.addItem(
                f"{orden.numero} — {orden.fecha}",
                orden.id,
            )

        self.orden.blockSignals(
            False,
        )

        self._cargar_lineas()

    def _cargar_lineas(self):

        orden_id = self.orden.currentData()

        lineas = self._pendientes.get(
            orden_id,
            [],
        )

        self.tabla.setRowCount(
            len(lineas),
        )

        for indice, linea in enumerate(
            lineas,
        ):

            self.tabla.setItem(
                indice,
                0,
                QTableWidgetItem(
                    linea["descripcion"],
                ),
            )

            self.tabla.setItem(
                indice,
                1,
                QTableWidgetItem(
                    f"{linea['cantidad']:,.2f}",
                ),
            )

            self.tabla.setItem(
                indice,
                2,
                QTableWidgetItem(
                    f"{linea['recibida']:,.2f}",
                ),
            )

            self.tabla.setItem(
                indice,
                3,
                QTableWidgetItem(
                    f"{linea['pendiente']:,.2f}",
                ),
            )

            spin = QDoubleSpinBox()

            spin.setMinimum(0)
            spin.setMaximum(
                linea["pendiente"],
            )

            spin.setDecimals(2)
            spin.setValue(
                linea["pendiente"],
            )

            spin.setProperty(
                "orden_detalle_id",
                linea["orden_detalle_id"],
            )

            self.tabla.setCellWidget(
                indice,
                4,
                spin,
            )

        self.tabla.resizeColumnsToContents()

    def _guardar(self):

        orden_id = self.orden.currentData()

        if orden_id is None:

            QMessageBox.warning(
                self,
                "Recepciones",
                "No hay órdenes pendientes.",
            )

            return

        bodega_id = self.bodega.currentData()

        if bodega_id is None:

            QMessageBox.warning(
                self,
                "Recepciones",
                "Seleccione una bodega.",
            )

            return

        lineas = []

        for fila in range(
            self.tabla.rowCount(),
        ):

            spin = self.tabla.cellWidget(
                fila,
                4,
            )

            if spin is None:

                continue

            cantidad = spin.value()

            if cantidad <= 0:

                continue

            lineas.append(
                {
                    "orden_detalle_id": spin.property(
                        "orden_detalle_id",
                    ),
                    "cantidad": cantidad,
                },
            )

        try:

            recepcion = (
                ServicioOrdenCompra
                .registrar_recepcion(
                    orden_id=orden_id,
                    bodega_id=bodega_id,
                    fecha=self.fecha.date().toPython(),
                    lineas=lineas,
                    observaciones=self.observaciones.text(),
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Recepciones",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Recepciones",
            f"Recepción {recepcion.numero} registrada.",
        )

        self.observaciones.clear()
        self._cargar_ordenes()
        self._cargar_historial()
