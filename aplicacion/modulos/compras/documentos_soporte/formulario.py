from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.base.page import Page
from aplicacion.framework.lookup import LookupWidget
from aplicacion.framework.ui.card import Card
from aplicacion.maestros.impuestos.celda_impuesto_iva import (
    CeldaImpuestoIVA,
)
from aplicacion.maestros.terceros.proveedor_lookup import (
    ProveedorLookup,
)
from aplicacion.modulos.compras.documentos_soporte.datasource import (
    DocumentoSoporteDataSource,
)
from aplicacion.modulos.compras.documentos_soporte.servicios import (
    ServicioDocumentoSoporte,
)
from aplicacion.modulos.compras.documentos_soporte.soporte_definition import (
    DocumentoSoporteDefinition,
)
from aplicacion.recursos.ui.botones import Botones


COL_DESCRIPCION = 0
COL_CANTIDAD = 1
COL_PRECIO = 2
COL_IMPUESTO = 3
COL_TOTAL = 4
COL_BORRAR = 5


class FormularioDocumentoSoporte(Page):

    definition = DocumentoSoporteDefinition

    guardado = Signal()
    cerrar = Signal()

    ancho = 1100
    alto = 620

    def __init__(
        self,
        id_registro=None,
        parent=None,
    ):

        self.id_registro = id_registro
        self.es_edicion = id_registro is not None
        self.datasource = DocumentoSoporteDataSource()

        super().__init__(
            parent=parent,
        )

        if not self.es_edicion:

            self._agregar_linea()

    def _crear_ui(self):

        super()._crear_ui()

        self.card = Card(
            "Documento soporte",
        )

        cabecera = QWidget()
        grid = QGridLayout(cabecera)

        self.txt_numero = QLineEdit()
        self.txt_numero.setPlaceholderText(
            "Automático",
        )

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDate(
            QDate.currentDate(),
        )

        self.proveedor = LookupWidget(
            ProveedorLookup(),
        )

        grid.addWidget(
            QLabel("Número"),
            0,
            0,
        )
        grid.addWidget(
            self.txt_numero,
            0,
            1,
        )
        grid.addWidget(
            QLabel("Fecha"),
            0,
            2,
        )
        grid.addWidget(
            self.fecha,
            0,
            3,
        )
        grid.addWidget(
            QLabel("Proveedor"),
            1,
            0,
        )
        grid.addWidget(
            self.proveedor,
            1,
            1,
            1,
            3,
        )

        self.card.contenido.addWidget(
            cabecera,
        )

        self.tabla = QTableWidget(
            0,
            6,
        )
        self.tabla.setHorizontalHeaderLabels(
            [
                "Descripción",
                "Cantidad",
                "Precio",
                "IVA",
                "Total",
                "",
            ],
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_DESCRIPCION,
            QHeaderView.Stretch,
        )

        self.card.contenido.addWidget(
            self.tabla,
        )

        acciones = QHBoxLayout()
        btn_agregar = Botones.aceptar()
        btn_agregar.setText("Agregar línea")
        btn_agregar.clicked.connect(
            self._agregar_linea,
        )
        acciones.addWidget(
            btn_agregar,
        )
        acciones.addStretch()

        self.lbl_subtotal = QLabel("Subtotal: $0")
        self.lbl_iva = QLabel("IVA: $0")
        self.lbl_total = QLabel("Total: $0")
        self.lbl_total.setStyleSheet(
            "font-weight:700;color:#1B4F8A;",
        )

        acciones.addWidget(
            self.lbl_subtotal,
        )
        acciones.addWidget(
            self.lbl_iva,
        )
        acciones.addWidget(
            self.lbl_total,
        )

        self.card.contenido.addLayout(
            acciones,
        )

        self.observaciones = QTextEdit()
        self.observaciones.setMaximumHeight(
            80,
        )
        self.card.contenido.addWidget(
            QLabel("Observaciones"),
        )
        self.card.contenido.addWidget(
            self.observaciones,
        )

        self.layout_principal.addWidget(
            self.card,
        )

        botones = QHBoxLayout()
        btn_guardar = Botones.aceptar()
        btn_guardar.setText("Guardar")
        btn_guardar.clicked.connect(
            self._guardar,
        )
        btn_cancelar = Botones.cerrar()
        btn_cancelar.clicked.connect(
            self.cerrar.emit,
        )
        botones.addStretch()
        botones.addWidget(
            btn_guardar,
        )
        botones.addWidget(
            btn_cancelar,
        )
        self.layout_principal.addLayout(
            botones,
        )

        if self.es_edicion:

            self._cargar()

    def _agregar_linea(self):

        fila = self.tabla.rowCount()
        self.tabla.insertRow(
            fila,
        )

        self.tabla.setItem(
            fila,
            COL_DESCRIPCION,
            QTableWidgetItem(""),
        )

        cantidad = QDoubleSpinBox()
        cantidad.setRange(
            0.01,
            999999,
        )
        cantidad.setValue(1)
        cantidad.valueChanged.connect(
            self._recalcular,
        )
        self.tabla.setCellWidget(
            fila,
            COL_CANTIDAD,
            cantidad,
        )

        precio = QDoubleSpinBox()
        precio.setRange(
            0,
            999999999,
        )
        precio.valueChanged.connect(
            self._recalcular,
        )
        self.tabla.setCellWidget(
            fila,
            COL_PRECIO,
            precio,
        )

        impuesto = CeldaImpuestoIVA()
        impuesto.combo.currentIndexChanged.connect(
            self._recalcular,
        )
        self.tabla.setCellWidget(
            fila,
            COL_IMPUESTO,
            impuesto,
        )

        self.tabla.setItem(
            fila,
            COL_TOTAL,
            QTableWidgetItem("0"),
        )

        btn = QPushButton("X")
        btn.clicked.connect(
            lambda: self._borrar_linea(
                btn,
            ),
        )
        self.tabla.setCellWidget(
            fila,
            COL_BORRAR,
            btn,
        )

        self._recalcular()

    def _borrar_linea(
        self,
        boton,
    ):

        for fila in range(
            self.tabla.rowCount(),
        ):

            if (
                self.tabla.cellWidget(
                    fila,
                    COL_BORRAR,
                )
                is boton
            ):

                self.tabla.removeRow(
                    fila,
                )
                break

        self._recalcular()

    def _recalcular(self):

        lineas = self._lineas_formulario()
        cabecera = {}
        ServicioDocumentoSoporte._aplicar_resumen(
            cabecera,
            lineas,
        )

        self.lbl_subtotal.setText(
            f"Subtotal: ${cabecera.get('subtotal', 0):,.0f}",
        )
        self.lbl_iva.setText(
            f"IVA: ${cabecera.get('iva', 0):,.0f}",
        )
        self.lbl_total.setText(
            f"Total: ${cabecera.get('total', 0):,.0f}",
        )

        for fila, linea in enumerate(
            lineas,
        ):

            item = self.tabla.item(
                fila,
                COL_TOTAL,
            )

            if item is not None:

                item.setText(
                    f"{linea['total_linea']:,.0f}",
                )

    def _lineas_formulario(self) -> list[dict]:

        lineas = []

        for fila in range(
            self.tabla.rowCount(),
        ):

            descripcion = (
                self.tabla.item(
                    fila,
                    COL_DESCRIPCION,
                )
                .text()
                .strip()
            )

            cantidad = self.tabla.cellWidget(
                fila,
                COL_CANTIDAD,
            ).value()

            precio = self.tabla.cellWidget(
                fila,
                COL_PRECIO,
            ).value()

            impuesto = self.tabla.cellWidget(
                fila,
                COL_IMPUESTO,
            ).valor()

            lineas.append(
                {
                    "descripcion": descripcion,
                    "cantidad": cantidad,
                    "precio_unitario": precio,
                    "impuesto_id": impuesto,
                    "total_linea": 0,
                }
            )

        return lineas

    def _cabecera_formulario(self) -> dict:

        return {
            "numero": self.txt_numero.text().strip(),
            "fecha": self.fecha.date().toPython(),
            "proveedor_id": self.proveedor.valor(),
            "observaciones": self.observaciones.toPlainText().strip(),
            "estado": "borrador",
            "activo": True,
        }

    def _cargar(self):

        documento = self.datasource.obtener_completa(
            self.id_registro,
        )

        if documento is None:

            return

        self.txt_numero.setText(
            documento.numero,
        )
        self.fecha.setDate(
            QDate(
                documento.fecha.year,
                documento.fecha.month,
                documento.fecha.day,
            ),
        )
        self.proveedor.establecer(
            documento.proveedor_id,
        )
        self.observaciones.setPlainText(
            documento.observaciones or "",
        )

        self.tabla.setRowCount(
            0,
        )

        for detalle in documento.detalles:

            self._agregar_linea()
            fila = self.tabla.rowCount() - 1

            self.tabla.item(
                fila,
                COL_DESCRIPCION,
            ).setText(
                detalle.descripcion,
            )

            self.tabla.cellWidget(
                fila,
                COL_CANTIDAD,
            ).setValue(
                detalle.cantidad,
            )

            self.tabla.cellWidget(
                fila,
                COL_PRECIO,
            ).setValue(
                detalle.precio_unitario,
            )

            self.tabla.cellWidget(
                fila,
                COL_IMPUESTO,
            )._cargar_por_id(
                detalle.impuesto_id,
            )

        self._recalcular()

    def _guardar(self):

        try:

            self.datasource.guardar_completa(
                self._cabecera_formulario(),
                self._lineas_formulario(),
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Documento soporte",
                str(error),
            )

            return

        self.guardado.emit()
