from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from aplicacion.modulos.tesoreria.conciliacion.servicios import (
    ServicioConciliacionBancaria,
)

_ETIQUETAS_TIPO_DOCUMENTO = {
    "comprobante_egreso": "Comprobante de egreso",
    "factura_compra": "Factura de compra",
    "recibo_caja": "Recibo de caja",
    "factura_venta": "Factura de venta",
}


class ConciliacionBancariaPage(QWidget):

    titulo = "Conciliación bancaria"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(
                "Importe extractos CSV y concilie "
                "automáticamente pagos con cartera "
                "y cuentas por pagar.",
            )
        )

        fila = QHBoxLayout()
        btn_importar = QPushButton(
            "Importar extracto CSV",
        )
        btn_importar.clicked.connect(
            self._importar,
        )
        btn_conciliar = QPushButton(
            "Conciliar automático",
        )
        btn_conciliar.clicked.connect(
            self._conciliar,
        )

        fila.addWidget(btn_importar)
        fila.addWidget(btn_conciliar)
        layout.addLayout(fila)

        self.lbl_resumen = QLabel("")
        layout.addWidget(self.lbl_resumen)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)

        self._construir_tab_pendientes()
        self._construir_tab_conciliadas()

        self._actualizar_resumen()
        self._cargar_pendientes()
        self._cargar_conciliadas()

    def _construir_tab_pendientes(self):
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)

        self.tabla_pendientes = QTableWidget(0, 4)
        self.tabla_pendientes.setHorizontalHeaderLabels(
            ["Fecha", "Descripción", "Tipo", "Valor"],
        )
        self.tabla_pendientes.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )
        self.tabla_pendientes.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows,
        )
        self.tabla_pendientes.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers,
        )
        self.tabla_pendientes.doubleClicked.connect(
            self._abrir_conciliar_manual,
        )
        layout.addWidget(self.tabla_pendientes, 1)

        btn_conciliar_manual = QPushButton(
            "Conciliar manualmente el movimiento seleccionado",
        )
        btn_conciliar_manual.clicked.connect(
            self._abrir_conciliar_manual,
        )
        layout.addWidget(btn_conciliar_manual)

        self.tabs.addTab(contenedor, "Pendientes")

    def _construir_tab_conciliadas(self):
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)

        self.tabla_conciliadas = QTableWidget(0, 4)
        self.tabla_conciliadas.setHorizontalHeaderLabels(
            ["Documento", "Número", "Valor", "Estado"],
        )
        self.tabla_conciliadas.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        self.tabla_conciliadas.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows,
        )
        self.tabla_conciliadas.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers,
        )
        layout.addWidget(self.tabla_conciliadas, 1)

        btn_deshacer = QPushButton(
            "Deshacer conciliación seleccionada",
        )
        btn_deshacer.clicked.connect(
            self._deshacer_seleccionada,
        )
        layout.addWidget(btn_deshacer)

        self.tabs.addTab(contenedor, "Conciliadas")

    def _actualizar_resumen(self):
        resumen = (
            ServicioConciliacionBancaria.resumen()
        )

        self.lbl_resumen.setText(
            f"Movimientos: {resumen['total']} | "
            f"Conciliados: {resumen['conciliados']} | "
            f"Pendientes: {resumen['pendientes']}"
        )

    def _cargar_pendientes(self):
        extractos = (
            ServicioConciliacionBancaria.listar_pendientes()
        )

        self.tabla_pendientes.setRowCount(
            len(extractos),
        )

        for fila, extracto in enumerate(extractos):
            item_fecha = QTableWidgetItem(
                str(extracto.fecha),
            )
            item_fecha.setData(
                Qt.ItemDataRole.UserRole,
                extracto.id,
            )

            self.tabla_pendientes.setItem(
                fila, 0, item_fecha,
            )
            self.tabla_pendientes.setItem(
                fila,
                1,
                QTableWidgetItem(
                    extracto.descripcion or "",
                ),
            )
            self.tabla_pendientes.setItem(
                fila,
                2,
                QTableWidgetItem(
                    extracto.tipo,
                ),
            )
            self.tabla_pendientes.setItem(
                fila,
                3,
                QTableWidgetItem(
                    f"${float(extracto.valor or 0):,.0f}",
                ),
            )

    def _cargar_conciliadas(self):
        conciliaciones = (
            ServicioConciliacionBancaria.listar_conciliadas()
        )

        self.tabla_conciliadas.setRowCount(
            len(conciliaciones),
        )

        for fila, registro in enumerate(conciliaciones):
            item_tipo = QTableWidgetItem(
                _ETIQUETAS_TIPO_DOCUMENTO.get(
                    registro.tipo_documento,
                    registro.tipo_documento,
                ),
            )
            item_tipo.setData(
                Qt.ItemDataRole.UserRole,
                registro.id,
            )

            self.tabla_conciliadas.setItem(
                fila, 0, item_tipo,
            )
            self.tabla_conciliadas.setItem(
                fila,
                1,
                QTableWidgetItem(
                    str(registro.documento_id),
                ),
            )
            self.tabla_conciliadas.setItem(
                fila,
                2,
                QTableWidgetItem(
                    f"${float(registro.valor or 0):,.0f}",
                ),
            )
            self.tabla_conciliadas.setItem(
                fila,
                3,
                QTableWidgetItem(
                    registro.estado or "",
                ),
            )

    def _importar(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Importar extracto",
            "",
            "CSV (*.csv);;Todos (*.*)",
        )

        if not ruta:
            return

        cantidad = (
            ServicioConciliacionBancaria.importar_csv(
                ruta,
            )
        )

        self.lbl_resumen.setText(
            f"Importados: {cantidad} movimiento(s).",
        )
        self._actualizar_resumen()
        self._cargar_pendientes()
        self._cargar_conciliadas()

    def _conciliar(self):
        resultado = (
            ServicioConciliacionBancaria
            .conciliar_automatico()
        )

        self.lbl_resumen.setText(
            f"Conciliados: {resultado['conciliados']} | "
            f"Pendientes: {resultado['pendientes']}"
        )
        self._actualizar_resumen()
        self._cargar_pendientes()
        self._cargar_conciliadas()

    def _abrir_conciliar_manual(self):
        fila = self.tabla_pendientes.currentRow()

        if fila < 0:
            QMessageBox.information(
                self,
                "Conciliar manualmente",
                "Seleccione un movimiento pendiente.",
            )
            return

        extracto_id = self.tabla_pendientes.item(
            fila, 0,
        ).data(Qt.ItemDataRole.UserRole)

        dialogo = _DialogoConciliarManual(
            extracto_id,
            parent=self,
        )

        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self._actualizar_resumen()
            self._cargar_pendientes()
            self._cargar_conciliadas()

    def _deshacer_seleccionada(self):
        fila = self.tabla_conciliadas.currentRow()

        if fila < 0:
            QMessageBox.information(
                self,
                "Deshacer conciliación",
                "Seleccione una conciliación.",
            )
            return

        conciliacion_id = self.tabla_conciliadas.item(
            fila, 0,
        ).data(Qt.ItemDataRole.UserRole)

        respuesta = QMessageBox.question(
            self,
            "Deshacer conciliación",
            "¿Deshacer esta conciliación? El movimiento "
            "bancario volverá a quedar pendiente.",
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        ServicioConciliacionBancaria.deshacer(
            conciliacion_id,
        )

        self._actualizar_resumen()
        self._cargar_pendientes()
        self._cargar_conciliadas()


class _DialogoConciliarManual(QDialog):

    def __init__(self, extracto_id: int, parent=None):
        super().__init__(parent)

        self._extracto_id = extracto_id

        self.setWindowTitle(
            "Conciliar manualmente",
        )
        self.resize(560, 420)

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(
                "Seleccione el documento que corresponde "
                "a este movimiento bancario:",
            )
        )

        self.tabla = QTableWidget(0, 4)
        self.tabla.setHorizontalHeaderLabels(
            ["Tipo", "Número", "Tercero", "Valor"],
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch,
        )
        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows,
        )
        self.tabla.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers,
        )
        layout.addWidget(self.tabla, 1)

        candidatos = (
            ServicioConciliacionBancaria.candidatos_documento(
                extracto_id,
            )
        )
        self._candidatos = candidatos

        self.tabla.setRowCount(len(candidatos))

        for fila, candidato in enumerate(candidatos):
            self.tabla.setItem(
                fila,
                0,
                QTableWidgetItem(
                    _ETIQUETAS_TIPO_DOCUMENTO.get(
                        candidato["tipo_documento"],
                        candidato["tipo_documento"],
                    ),
                ),
            )
            self.tabla.setItem(
                fila,
                1,
                QTableWidgetItem(
                    candidato["numero"] or "",
                ),
            )
            self.tabla.setItem(
                fila,
                2,
                QTableWidgetItem(
                    candidato["tercero"] or "",
                ),
            )
            self.tabla.setItem(
                fila,
                3,
                QTableWidgetItem(
                    f"${candidato['valor']:,.0f}",
                ),
            )

        botones = QHBoxLayout()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)

        btn_conciliar = QPushButton("Conciliar")
        btn_conciliar.clicked.connect(self._confirmar)

        botones.addStretch(1)
        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_conciliar)
        layout.addLayout(botones)

    def _confirmar(self):
        fila = self.tabla.currentRow()

        if fila < 0:
            QMessageBox.information(
                self,
                "Conciliar manualmente",
                "Seleccione un documento de la lista.",
            )
            return

        candidato = self._candidatos[fila]

        try:
            ServicioConciliacionBancaria.conciliar_manual(
                self._extracto_id,
                candidato["tipo_documento"],
                candidato["documento_id"],
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Conciliar manualmente",
                str(error),
            )
            return

        self.accept()
