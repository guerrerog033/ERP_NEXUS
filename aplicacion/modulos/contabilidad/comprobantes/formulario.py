from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from aplicacion.framework.base.page import Page
from aplicacion.framework.lookup import LookupWidget
from aplicacion.modulos.contabilidad.comprobantes.datasource import (
    ComprobanteDataSource,
)
from aplicacion.modulos.contabilidad.plan_cuentas.cuenta_lookup import (
    PlanCuentaLookup,
)
from aplicacion.recursos.ui.botones import Botones


class FormularioComprobante(Page):

    titulo = "Comprobante contable"

    ancho = 980
    alto = 680

    guardado = Signal()
    cerrar = Signal()

    COL_CUENTA = 0
    COL_DEBITO = 1
    COL_CREDITO = 2
    COL_DESC = 3

    def __init__(
        self,
        id_registro=None,
        parent=None,
    ):

        self.id_registro = id_registro
        self.datasource = ComprobanteDataSource()

        super().__init__(
            parent=parent,
        )

        if id_registro is not None:

            self._cargar_registro()

    def _crear_ui(self):

        super()._crear_ui()

        formulario = QFormLayout()

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDate(date.today())

        self.descripcion = QTextEdit()
        self.descripcion.setMaximumHeight(70)

        formulario.addRow(
            "Fecha",
            self.fecha,
        )

        formulario.addRow(
            "Descripción",
            self.descripcion,
        )

        self.layout_principal.addLayout(
            formulario,
        )

        self.lbl_totales = QLabel(
            "Débitos: 0.00 | Créditos: 0.00 | Diferencia: 0.00",
        )

        self.layout_principal.addWidget(
            self.lbl_totales,
        )

        self.tabla = QTableWidget(
            0,
            4,
        )

        self.tabla.setHorizontalHeaderLabels(
            [
                "Cuenta",
                "Débito",
                "Crédito",
                "Detalle",
            ],
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            self.COL_CUENTA,
            QHeaderView.Stretch,
        )

        self.layout_principal.addWidget(
            self.tabla,
            1,
        )

        acciones = QHBoxLayout()

        self.btn_agregar = QPushButton(
            "Agregar línea",
        )

        self.btn_agregar.clicked.connect(
            self._agregar_linea,
        )

        self.btn_quitar = QPushButton(
            "Quitar línea",
        )

        self.btn_quitar.clicked.connect(
            self._quitar_linea,
        )

        acciones.addWidget(
            self.btn_agregar,
        )

        acciones.addWidget(
            self.btn_quitar,
        )

        acciones.addStretch()

        self.layout_principal.addLayout(
            acciones,
        )

        botones = QHBoxLayout()
        botones.addStretch()

        self.btn_guardar = Botones.guardar()
        self.btn_cancelar = Botones.cerrar()

        self.btn_guardar.clicked.connect(
            self._guardar,
        )

        self.btn_cancelar.clicked.connect(
            self.cerrar.emit,
        )

        botones.addWidget(
            self.btn_guardar,
        )

        botones.addWidget(
            self.btn_cancelar,
        )

        self.layout_principal.addLayout(
            botones,
        )

        if self.id_registro is None:

            self._agregar_linea()
            self._agregar_linea()

    def _agregar_linea(self):

        fila = self.tabla.rowCount()

        self.tabla.insertRow(
            fila,
        )

        lookup = LookupWidget(
            PlanCuentaLookup(),
        )

        self.tabla.setCellWidget(
            fila,
            self.COL_CUENTA,
            lookup,
        )

        debito = QDoubleSpinBox()
        debito.setMaximum(999999999999)
        debito.setDecimals(2)
        debito.valueChanged.connect(
            self._actualizar_totales,
        )

        credito = QDoubleSpinBox()
        credito.setMaximum(999999999999)
        credito.setDecimals(2)
        credito.valueChanged.connect(
            self._actualizar_totales,
        )

        self.tabla.setCellWidget(
            fila,
            self.COL_DEBITO,
            debito,
        )

        self.tabla.setCellWidget(
            fila,
            self.COL_CREDITO,
            credito,
        )

        self.tabla.setItem(
            fila,
            self.COL_DESC,
            QTableWidgetItem(""),
        )

        self._actualizar_totales()

    def _quitar_linea(self):

        fila = self.tabla.currentRow()

        if fila < 0:

            return

        self.tabla.removeRow(
            fila,
        )

        self._actualizar_totales()

    def _actualizar_totales(self):

        total_debito = 0.0
        total_credito = 0.0

        for fila in range(
            self.tabla.rowCount(),
        ):

            debito = self.tabla.cellWidget(
                fila,
                self.COL_DEBITO,
            )

            credito = self.tabla.cellWidget(
                fila,
                self.COL_CREDITO,
            )

            if debito is not None:

                total_debito += float(
                    debito.value(),
                )

            if credito is not None:

                total_credito += float(
                    credito.value(),
                )

        diferencia = total_debito - total_credito

        self.lbl_totales.setText(
            "Débitos: "
            f"{total_debito:,.2f} | Créditos: "
            f"{total_credito:,.2f} | Diferencia: "
            f"{diferencia:,.2f}",
        )

    def _lineas(self) -> list[dict]:

        lineas = []

        for fila in range(
            self.tabla.rowCount(),
        ):

            lookup = self.tabla.cellWidget(
                fila,
                self.COL_CUENTA,
            )

            cuenta_id = None

            if lookup is not None:

                cuenta_id = lookup.valor()

            debito = self.tabla.cellWidget(
                fila,
                self.COL_DEBITO,
            )

            credito = self.tabla.cellWidget(
                fila,
                self.COL_CREDITO,
            )

            item_desc = self.tabla.item(
                fila,
                self.COL_DESC,
            )

            lineas.append(
                {
                    "cuenta_id": cuenta_id,
                    "debito": float(
                        debito.value()
                        if debito
                        else 0,
                    ),
                    "credito": float(
                        credito.value()
                        if credito
                        else 0,
                    ),
                    "descripcion": (
                        item_desc.text()
                        if item_desc
                        else ""
                    ),
                },
            )

        return lineas

    def _cargar_registro(self):

        asiento = self.datasource.obtener_completo(
            self.id_registro,
        )

        if asiento is None:

            return

        self.fecha.setDate(
            asiento.fecha,
        )

        self.descripcion.setPlainText(
            asiento.descripcion or "",
        )

        self.tabla.setRowCount(
            0,
        )

        for detalle in asiento.detalles:

            self._agregar_linea()

            fila = self.tabla.rowCount() - 1

            lookup = self.tabla.cellWidget(
                fila,
                self.COL_CUENTA,
            )

            if lookup is not None:

                lookup.establecer(
                    detalle.cuenta_id,
                )

            debito = self.tabla.cellWidget(
                fila,
                self.COL_DEBITO,
            )

            credito = self.tabla.cellWidget(
                fila,
                self.COL_CREDITO,
            )

            if debito is not None:

                debito.setValue(
                    float(
                        detalle.debito or 0,
                    ),
                )

            if credito is not None:

                credito.setValue(
                    float(
                        detalle.credito or 0,
                    ),
                )

            item_desc = self.tabla.item(
                fila,
                self.COL_DESC,
            )

            if item_desc is not None:

                item_desc.setText(
                    detalle.descripcion or "",
                )

        self._actualizar_totales()

    def _guardar(self):

        try:

            self.datasource.guardar(
                {
                    "cabecera": {
                        "fecha": self.fecha.date().toPython(),
                        "descripcion": self.descripcion.toPlainText(),
                    },
                    "lineas": self._lineas(),
                },
                self.id_registro,
            )

        except Exception as error:

            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self,
                "Comprobante",
                str(error),
            )

            return

        self.guardado.emit()
        self.cerrar.emit()
