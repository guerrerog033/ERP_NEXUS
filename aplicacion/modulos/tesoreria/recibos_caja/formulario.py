from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from aplicacion.framework.base.page import Page
from aplicacion.framework.lookup import LookupWidget
from aplicacion.maestros.terceros.cliente_lookup import (
    ClienteLookup,
)
from aplicacion.modulos.tesoreria.recibos_caja.datasource import (
    ReciboCajaDataSource,
)
from aplicacion.modulos.tesoreria.recibos_caja.formatos_impresion import (
    formatos_combo,
)
from aplicacion.modulos.tesoreria.recibos_caja.integracion import (
    IntegracionReciboCaja,
)
from aplicacion.modulos.tesoreria.recibos_caja.recibo_definition import (
    ReciboCajaDefinition,
)
from aplicacion.modulos.tesoreria.recibos_caja.servicios import (
    FORMAS_PAGO,
)
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)
from aplicacion.recursos.ui.botones import Botones


class FormularioReciboCaja(Page):

    titulo = "Recibo de caja"

    definition = ReciboCajaDefinition

    ancho = 920
    alto = 620

    guardado = Signal()
    cerrar = Signal()

    COL_FACTURA = 0
    COL_FECHA = 1
    COL_TOTAL = 2
    COL_SALDO = 3
    COL_PAGAR = 4

    def __init__(
        self,
        id_registro=None,
        parent=None,
    ):

        self.id_registro = id_registro
        self.datasource = ReciboCajaDataSource()
        self._facturas: list = []

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

        self.cliente = LookupWidget(
            ClienteLookup(),
        )
        self.cliente.seleccionado.connect(
            self._cargar_facturas,
        )

        self.forma_pago = QComboBox()

        for etiqueta, codigo in FORMAS_PAGO:

            self.forma_pago.addItem(
                etiqueta,
                codigo,
            )

        self.observaciones = QTextEdit()
        self.observaciones.setMaximumHeight(70)

        self.formato = QComboBox()

        for etiqueta, codigo in formatos_combo():

            self.formato.addItem(
                etiqueta,
                codigo,
            )

        indice_formato = self.formato.findData(
            ServicioCotizacion.formato_predeterminado(),
        )

        if indice_formato >= 0:

            self.formato.setCurrentIndex(
                indice_formato,
            )

        formulario.addRow(
            "Fecha",
            self.fecha,
        )
        formulario.addRow(
            "Cliente",
            self.cliente,
        )
        formulario.addRow(
            "Forma de pago",
            self.forma_pago,
        )
        formulario.addRow(
            "Formato de impresión",
            self.formato,
        )
        formulario.addRow(
            "Observaciones",
            self.observaciones,
        )

        self.chk_anticipo = QCheckBox(
            "Abono / anticipo sin factura",
        )

        self.valor_abono = QDoubleSpinBox()
        self.valor_abono.setRange(
            0,
            999_999_999_999,
        )
        self.valor_abono.setDecimals(
            2,
        )
        self.valor_abono.setPrefix(
            "$ ",
        )
        self.valor_abono.valueChanged.connect(
            self._actualizar_total,
        )

        formulario.addRow(
            "",
            self.chk_anticipo,
        )
        formulario.addRow(
            "Valor del abono",
            self.valor_abono,
        )

        self.chk_anticipo.toggled.connect(
            self._actualizar_modo_anticipo,
        )

        self.layout_principal.addLayout(
            formulario,
        )

        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(
            [
                "Factura",
                "Fecha",
                "Total",
                "Saldo",
                "Valor a pagar",
            ],
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch,
        )

        self.layout_principal.addWidget(
            self.tabla,
        )

        self.lbl_total = QLabel("Total recibo: $ 0")
        self.lbl_total.setAlignment(
            Qt.AlignRight,
        )

        self.layout_principal.addWidget(
            self.lbl_total,
        )

        botones = QHBoxLayout()
        botones.addStretch()

        self.btn_guardar = Botones.guardar()
        self.btn_guardar.clicked.connect(
            self._guardar,
        )

        btn_cancelar = Botones.cancelar()
        btn_cancelar.clicked.connect(
            self.cerrar.emit,
        )

        botones.addWidget(
            self.btn_guardar,
        )
        botones.addWidget(
            btn_cancelar,
        )

        self.layout_principal.addLayout(
            botones,
        )

        self._actualizar_modo_anticipo(
            False,
        )

    def _actualizar_modo_anticipo(
        self,
        anticipo: bool,
    ) -> None:

        self.tabla.setVisible(
            not anticipo,
        )
        self.valor_abono.setEnabled(
            anticipo,
        )

        self._actualizar_total()

    def _cargar_registro(self):

        recibo = self.datasource.obtener_completo(
            self.id_registro,
        )

        if recibo is None:

            return

        if recibo.contabilizado:

            self.btn_guardar.setEnabled(
                False,
            )

        self.fecha.setDate(
            recibo.fecha,
        )
        self.cliente.setValue(
            recibo.cliente_id,
        )

        indice = self.forma_pago.findData(
            recibo.forma_pago,
        )

        if indice >= 0:

            self.forma_pago.setCurrentIndex(
                indice,
            )

        if recibo.formato_impresion:

            indice_formato = self.formato.findData(
                recibo.formato_impresion,
            )

            if indice_formato >= 0:

                self.formato.setCurrentIndex(
                    indice_formato,
                )

        self.observaciones.setPlainText(
            recibo.observaciones or "",
        )

        if not recibo.detalles:

            self.chk_anticipo.setChecked(
                True,
            )
            self.valor_abono.setValue(
                float(
                    recibo.valor_total or 0,
                ),
            )

            self._actualizar_modo_anticipo(
                True,
            )

            return

        self._cargar_facturas()

        valores = {
            detalle.factura_venta_id: detalle.valor_aplicado
            for detalle in recibo.detalles
        }

        for fila in range(
            self.tabla.rowCount(),
        ):

            item = self.tabla.item(
                fila,
                self.COL_FACTURA,
            )

            if item is None:

                continue

            factura_id = item.data(
                Qt.UserRole,
            )

            spin = self.tabla.cellWidget(
                fila,
                self.COL_PAGAR,
            )

            if (
                spin is not None
                and factura_id in valores
            ):

                spin.setValue(
                    float(
                        valores[factura_id],
                    ),
                )

        self._actualizar_total()

    def _cargar_facturas(self):

        cliente_id = self.cliente.valor()

        self.tabla.setRowCount(0)
        self._facturas = []

        if not cliente_id:

            self._actualizar_total()

            return

        self._facturas = (
            self.datasource.listar_facturas_pendientes(
                int(cliente_id),
            )
        )

        self.tabla.setRowCount(
            len(self._facturas),
        )

        for fila, factura in enumerate(
            self._facturas,
        ):

            item_numero = QTableWidgetItem(
                factura.numero,
            )
            item_numero.setData(
                Qt.UserRole,
                factura.id,
            )
            item_numero.setFlags(
                Qt.ItemIsEnabled
                | Qt.ItemIsSelectable,
            )

            item_fecha = QTableWidgetItem(
                factura.fecha.strftime(
                    "%d/%m/%Y",
                ),
            )
            item_fecha.setFlags(
                Qt.ItemIsEnabled
                | Qt.ItemIsSelectable,
            )

            item_total = QTableWidgetItem(
                f"{float(factura.total or 0):,.2f}",
            )
            item_total.setTextAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter,
            )
            item_total.setFlags(
                Qt.ItemIsEnabled
                | Qt.ItemIsSelectable,
            )

            saldo = float(
                factura.saldo_pendiente or 0,
            )

            item_saldo = QTableWidgetItem(
                f"{saldo:,.2f}",
            )
            item_saldo.setTextAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter,
            )
            item_saldo.setFlags(
                Qt.ItemIsEnabled
                | Qt.ItemIsSelectable,
            )

            spin = QDoubleSpinBox()
            spin.setRange(0, saldo)
            spin.setDecimals(2)
            spin.setMaximumWidth(140)
            spin.valueChanged.connect(
                self._actualizar_total,
            )

            self.tabla.setItem(
                fila,
                self.COL_FACTURA,
                item_numero,
            )
            self.tabla.setItem(
                fila,
                self.COL_FECHA,
                item_fecha,
            )
            self.tabla.setItem(
                fila,
                self.COL_TOTAL,
                item_total,
            )
            self.tabla.setItem(
                fila,
                self.COL_SALDO,
                item_saldo,
            )
            self.tabla.setCellWidget(
                fila,
                self.COL_PAGAR,
                spin,
            )

        self._actualizar_total()

    def _actualizar_total(self):

        if self.chk_anticipo.isChecked():

            total = float(
                self.valor_abono.value(),
            )

            self.lbl_total.setText(
                f"Total recibo: $ {total:,.2f}",
            )

            return

        total = 0.0

        for fila in range(
            self.tabla.rowCount(),
        ):

            spin = self.tabla.cellWidget(
                fila,
                self.COL_PAGAR,
            )

            if spin is not None:

                total += float(
                    spin.value(),
                )

        self.lbl_total.setText(
            f"Total recibo: $ {total:,.2f}",
        )

    def _lineas(self) -> list[dict]:

        lineas: list[dict] = []

        for fila in range(
            self.tabla.rowCount(),
        ):

            item = self.tabla.item(
                fila,
                self.COL_FACTURA,
            )

            spin = self.tabla.cellWidget(
                fila,
                self.COL_PAGAR,
            )

            if (
                item is None
                or spin is None
            ):

                continue

            valor = float(
                spin.value(),
            )

            if valor <= 0:

                continue

            lineas.append(
                {
                    "factura_venta_id": int(
                        item.data(
                            Qt.UserRole,
                        ),
                    ),
                    "valor_aplicado": valor,
                },
            )

        return lineas

    def _guardar(self):

        cliente_id = self.cliente.valor()

        if not cliente_id:

            QMessageBox.warning(
                self,
                "Cliente requerido",
                "Seleccione un cliente.",
            )

            return

        cabecera = {
            "fecha": self.fecha.date().toPython(),
            "cliente_id": int(cliente_id),
            "forma_pago": self.forma_pago.currentData(),
            "formato_impresion": self.formato.currentData(),
            "observaciones": (
                self.observaciones.toPlainText().strip()
            ),
        }

        if self.chk_anticipo.isChecked():

            cabecera["es_anticipo"] = True
            cabecera["valor_total"] = float(
                self.valor_abono.value(),
            )
            lineas: list[dict] = []

        else:

            lineas = self._lineas()

        try:

            recibo = self.datasource.guardar_completo(
                cabecera,
                lineas,
                id_registro=self.id_registro,
            )

            IntegracionReciboCaja.contabilizar_automatico(
                recibo.id,
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Recibo guardado",
            f"Recibo {recibo.numero} guardado correctamente.",
        )

        self.guardado.emit()
        self.cerrar.emit()
