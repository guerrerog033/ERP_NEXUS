from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, QTimer, Signal
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

        if not getattr(
            self,
            "_foco_inicial_aplicado",
            False,
        ):

            self._foco_inicial_aplicado = True

            QTimer.singleShot(
                0,
                self._aplicar_foco_inicial,
            )

    def _aplicar_foco_inicial(
        self,
    ) -> None:
        """
        Al abrir: si falta el proveedor, foco en su selector; si ya
        está, foco en la descripción de la primera línea (celda de
        tabla, no widget) para empezar a cargar ítems de una.
        """

        if not self.proveedor.valor():

            self.proveedor.btn.setFocus()

            return

        if self.tabla.rowCount() == 0:

            self.proveedor.btn.setFocus()

            return

        item = self.tabla.item(
            0,
            COL_DESCRIPCION,
        )

        if item is None:

            self.proveedor.btn.setFocus()

            return

        self.tabla.setCurrentItem(
            item,
        )
        self.tabla.editItem(
            item,
        )

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

        for columna, widget in (
            (COL_CANTIDAD, cantidad),
            (COL_PRECIO, precio),
            (COL_IMPUESTO, impuesto),
        ):

            self._conectar_enter_avanza(
                widget,
                columna,
            )

        self._recalcular()

    _ORDEN_COLUMNAS_FILA = (
        COL_CANTIDAD,
        COL_PRECIO,
        COL_IMPUESTO,
    )

    @staticmethod
    def _enfocar_widget(
        widget,
    ) -> None:

        combo_interno = getattr(
            widget,
            "combo",
            widget,
        )

        editor = getattr(
            combo_interno,
            "lineEdit",
            lambda: None,
        )()

        (editor or widget).setFocus()

    def _avanzar_desde(
        self,
        widget,
        columna: int,
    ) -> None:
        """
        Busca en qué fila está ``widget`` en este momento (no se
        guarda el índice al conectar la señal, porque agregar o
        borrar filas lo correría) y le pone foco al siguiente campo
        de la planilla: la próxima columna de la misma fila, o la
        cantidad de la fila de abajo si ya era la última columna
        (la descripción es una celda de tabla, no un widget, así
        que no participa de esta cadena).
        """

        for fila in range(
            self.tabla.rowCount(),
        ):

            if (
                self.tabla.cellWidget(
                    fila,
                    columna,
                )
                is not widget
            ):

                continue

            indice = self._ORDEN_COLUMNAS_FILA.index(
                columna,
            )

            if indice + 1 < len(
                self._ORDEN_COLUMNAS_FILA,
            ):

                siguiente = self.tabla.cellWidget(
                    fila,
                    self._ORDEN_COLUMNAS_FILA[
                        indice + 1
                    ],
                )

            else:

                siguiente = self.tabla.cellWidget(
                    fila + 1,
                    COL_CANTIDAD,
                )

            if siguiente is not None:

                self._enfocar_widget(
                    siguiente,
                )

            return

    def _conectar_enter_avanza(
        self,
        widget,
        columna: int,
    ) -> None:
        """
        Enter en cantidad/precio/IVA avanza al siguiente como en
        una planilla, en vez de no hacer nada.
        """

        manejador = (
            lambda w=widget, c=columna: self._avanzar_desde(
                w,
                c,
            )
        )

        combo_interno = getattr(
            widget,
            "combo",
            widget,
        )

        editor = getattr(
            combo_interno,
            "lineEdit",
            lambda: None,
        )()

        if editor is not None:

            editor.returnPressed.connect(
                manejador,
            )

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

    def _recalcular(
        self,
    ):
        """
        Punto de entrada de todas las señales de edición. Coalescea
        los recálculos en una sola pasada tras una pausa corta para
        no recorrer toda la tabla en cada tecla / rueda del mouse.
        """

        timer = getattr(
            self,
            "_timer_totales",
            None,
        )

        if timer is None:

            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.setInterval(120)
            timer.timeout.connect(
                self._recalcular_ahora,
            )
            self._timer_totales = timer

        timer.start()

    def _recalcular_ahora(self):

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

    @staticmethod
    def _linea_vacia(
        linea: dict,
    ) -> bool:

        return not (
            str(
                linea.get(
                    "descripcion",
                )
                or "",
            ).strip()
            or float(
                linea.get(
                    "cantidad",
                )
                or 0,
            )
            or float(
                linea.get(
                    "precio_unitario",
                )
                or 0,
            )
        )

    def _lineas_no_vacias(
        self,
        lineas: list[dict],
    ) -> list[dict]:

        return [
            linea
            for linea in lineas
            if not FormularioDocumentoSoporte._linea_vacia(
                linea,
            )
        ]

    def _validar_documento_basico(
        self,
        cabecera: dict,
        lineas: list[dict],
    ):
        """
        Validación en pantalla antes de golpear el datasource.
        Devuelve ``(mensaje, widget_a_enfocar)`` o ``(None, None)``
        si está todo bien.
        """

        if not cabecera.get(
            "proveedor_id",
        ):

            return (
                "Seleccione el proveedor antes de guardar.",
                self.proveedor.btn,
            )

        if not lineas:

            return (
                "Agregue al menos un ítem con descripción y "
                "cantidad.",
                self.tabla,
            )

        for indice, linea in enumerate(
            lineas,
            start=1,
        ):

            if not str(
                linea.get(
                    "descripcion",
                )
                or "",
            ).strip():

                return (
                    f"El ítem {indice} no tiene descripción.",
                    self.tabla,
                )

            if (
                float(
                    linea.get(
                        "cantidad",
                    )
                    or 0,
                )
                <= 0
            ):

                return (
                    f"El ítem {indice} debe tener cantidad "
                    "mayor que cero.",
                    self.tabla,
                )

            if (
                float(
                    linea.get(
                        "precio_unitario",
                    )
                    or 0,
                )
                < 0
            ):

                return (
                    f"El ítem {indice} tiene un precio negativo.",
                    self.tabla,
                )

        return (None, None)

    def _guardar(self):

        cabecera = self._cabecera_formulario()
        lineas = self._lineas_no_vacias(
            self._lineas_formulario(),
        )

        mensaje, foco = self._validar_documento_basico(
            cabecera,
            lineas,
        )

        if mensaje:

            QMessageBox.warning(
                self,
                "Datos incompletos",
                mensaje,
            )

            if foco is not None:

                foco.setFocus()

            return

        try:

            self.datasource.guardar_completa(
                cabecera,
                lineas,
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
