from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
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
from aplicacion.maestros.impuestos.celda_retencion_combo import (
    CeldaRetencionCombo,
)
from aplicacion.maestros.impuestos.retencion_lookup import (
    ReteICALookup,
    ReteIVALookup,
    RetefuenteLookup,
)
from aplicacion.maestros.terceros.proveedor_lookup import (
    ProveedorLookup,
)
from aplicacion.modulos.compras.facturas.datasource import (
    FacturaCompraDataSource,
)
from aplicacion.modulos.compras.facturas.factura_definition import (
    FacturaCompraDefinition,
)
from aplicacion.modulos.compras.facturas.formatos_impresion import (
    formatos_combo,
)
from aplicacion.modulos.compras.facturas.servicios import (
    ServicioFacturaCompra,
)
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)
from aplicacion.recursos.ui.botones import Botones


COL_DESCRIPCION = 0
COL_CANTIDAD = 1
COL_PRECIO = 2
COL_IMPUESTO = 3
COL_TOTAL = 4
COL_BORRAR = 5


class FormularioFacturaCompra(Page):

    definition = FacturaCompraDefinition

    guardado = Signal()

    cerrar = Signal()

    ancho = 1180

    alto = 640

    def __init__(
        self,
        id_registro=None,
        parent=None,
    ):

        self.id_registro = id_registro
        self.es_edicion = id_registro is not None
        self.datasource = FacturaCompraDataSource()
        self._ruta_xml_pendiente = ""

        super().__init__(
            parent=parent,
        )

        if parent is not None:

            self.setParent(
                parent,
            )

        self._cargar_datos()

    def _crear_ui(self):

        super()._crear_ui()

        cabecera = Card(
            "Datos de la factura de compra",
        )

        panel_cabecera = QWidget()

        grid = QGridLayout(
            panel_cabecera,
        )

        grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        grid.setHorizontalSpacing(
            12,
        )

        grid.setVerticalSpacing(
            8,
        )

        self.txt_numero = QLineEdit()
        self.txt_numero.setReadOnly(
            True,
        )

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(
            True,
        )
        self.fecha.setDate(
            QDate.currentDate(),
        )

        self.proveedor = LookupWidget(
            ProveedorLookup(),
        )

        self.proveedor.seleccionado.connect(
            self._on_proveedor_seleccionado,
        )

        self.txt_nit = QLineEdit()
        self.txt_razon = QLineEdit()
        self.txt_numero_proveedor = QLineEdit()
        self.txt_prefijo = QLineEdit()
        self.txt_consecutivo = QLineEdit()
        self.txt_cufe = QLineEdit()
        self.observaciones = QTextEdit()
        self.observaciones.setMaximumHeight(
            60,
        )

        fila = 0

        grid.addWidget(
            QLabel("Número interno"),
            fila,
            0,
        )
        grid.addWidget(
            self.txt_numero,
            fila,
            1,
        )
        grid.addWidget(
            QLabel("Fecha"),
            fila,
            2,
        )
        grid.addWidget(
            self.fecha,
            fila,
            3,
        )

        fila += 1

        grid.addWidget(
            QLabel("Proveedor"),
            fila,
            0,
        )
        grid.addWidget(
            self.proveedor,
            fila,
            1,
            1,
            3,
        )

        fila += 1

        grid.addWidget(
            QLabel("NIT"),
            fila,
            0,
        )
        grid.addWidget(
            self.txt_nit,
            fila,
            1,
        )
        grid.addWidget(
            QLabel("Razón social"),
            fila,
            2,
        )
        grid.addWidget(
            self.txt_razon,
            fila,
            3,
        )

        fila += 1

        grid.addWidget(
            QLabel("Factura proveedor"),
            fila,
            0,
        )
        grid.addWidget(
            self.txt_numero_proveedor,
            fila,
            1,
        )
        grid.addWidget(
            QLabel("Prefijo"),
            fila,
            2,
        )
        grid.addWidget(
            self.txt_prefijo,
            fila,
            3,
        )

        fila += 1

        grid.addWidget(
            QLabel("Consecutivo"),
            fila,
            0,
        )
        grid.addWidget(
            self.txt_consecutivo,
            fila,
            1,
        )
        grid.addWidget(
            QLabel("CUFE"),
            fila,
            2,
        )
        grid.addWidget(
            self.txt_cufe,
            fila,
            3,
        )

        fila += 1

        grid.addWidget(
            QLabel("Observaciones"),
            fila,
            0,
        )
        grid.addWidget(
            self.observaciones,
            fila,
            1,
            1,
            3,
        )

        fila += 1

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

        grid.addWidget(
            QLabel("Formato de impresión"),
            fila,
            0,
        )
        grid.addWidget(
            self.formato,
            fila,
            1,
        )

        fila += 1

        self.celda_retefuente = CeldaRetencionCombo(
            lookup=RetefuenteLookup(),
        )
        self.celda_reteica = CeldaRetencionCombo(
            lookup=ReteICALookup(),
        )
        self.celda_reteiva = CeldaRetencionCombo(
            lookup=ReteIVALookup(),
        )

        grid.addWidget(
            QLabel("Retefuente"),
            fila,
            0,
        )
        grid.addWidget(
            self.celda_retefuente,
            fila,
            1,
        )
        grid.addWidget(
            QLabel("ReteICA"),
            fila,
            2,
        )
        grid.addWidget(
            self.celda_reteica,
            fila,
            3,
        )

        fila += 1

        grid.addWidget(
            QLabel("ReteIVA"),
            fila,
            0,
        )
        grid.addWidget(
            self.celda_reteiva,
            fila,
            1,
        )

        for celda in (
            self.celda_retefuente,
            self.celda_reteica,
            self.celda_reteiva,
        ):

            celda.cambiado.connect(
                self._recalcular_totales,
            )

        grid.setColumnStretch(
            1,
            1,
        )

        grid.setColumnStretch(
            3,
            1,
        )

        grid.setColumnMinimumWidth(
            0,
            120,
        )

        grid.setColumnMinimumWidth(
            2,
            120,
        )

        cabecera.agregar_widget(
            panel_cabecera,
        )

        cabecera.layout_principal.setContentsMargins(
            16,
            20,
            16,
            20,
        )

        self.setMinimumWidth(
            self.ancho,
        )

        self.agregar_widget(
            cabecera,
        )

        lineas_card = Card(
            "Líneas",
        )

        self.tabla = QTableWidget(
            0,
            6,
        )

        self.tabla.setHorizontalHeaderLabels(
            [
                "Descripción",
                "Cantidad",
                "Precio unit.",
                "IVA",
                "Total",
                "",
            ],
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_DESCRIPCION,
            QHeaderView.ResizeMode.Stretch,
        )

        lineas_card.agregar_widget(
            self.tabla,
        )

        self.agregar_widget(
            lineas_card,
        )

        acciones_lineas = QHBoxLayout()

        btn_agregar = QPushButton(
            "Agregar línea",
        )

        btn_agregar.clicked.connect(
            self._agregar_fila,
        )

        btn_importar = QPushButton(
            "Importar XML DIAN",
        )

        btn_importar.clicked.connect(
            self._importar_xml,
        )

        acciones_lineas.addWidget(
            btn_agregar,
        )
        acciones_lineas.addWidget(
            btn_importar,
        )
        acciones_lineas.addStretch()

        self.lbl_subtotal = QLabel(
            "Subtotal: $ 0",
        )
        self.lbl_iva = QLabel(
            "IVA: $ 0",
        )
        self.lbl_total = QLabel(
            "Total: $ 0",
        )

        acciones_lineas.addWidget(
            self.lbl_subtotal,
        )
        acciones_lineas.addWidget(
            self.lbl_iva,
        )
        acciones_lineas.addWidget(
            self.lbl_total,
        )

        self.agregar_layout(
            acciones_lineas,
        )

        barra = QHBoxLayout()

        barra.addStretch()

        btn_guardar = Botones.guardar()

        btn_guardar.clicked.connect(
            self.guardar,
        )

        btn_cerrar = Botones.cerrar()

        btn_cerrar.clicked.connect(
            self.cerrar.emit,
        )

        barra.addWidget(
            btn_guardar,
        )
        barra.addWidget(
            btn_cerrar,
        )

        self.agregar_layout(
            barra,
        )

        if not self.es_edicion:

            self.txt_numero.setText(
                ServicioFacturaCompra.generar_numero(),
            )

            self._agregar_fila()

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
        está, foco en la descripción de la primera línea para
        empezar a cargar ítems de una.
        """

        if not self.proveedor.valor():

            self.proveedor.btn.setFocus()

            return

        descripcion = self._widget_fila(
            0,
            COL_DESCRIPCION,
        )

        if descripcion is not None:

            descripcion.setFocus()

        else:

            self.proveedor.btn.setFocus()

    def _on_proveedor_seleccionado(
        self,
        resultado,
    ):

        if resultado is None:

            return

        proveedor = resultado.objeto

        if proveedor is None:

            return

        self.txt_nit.setText(
            proveedor.numero_documento
            or "",
        )

        self.txt_razon.setText(
            proveedor.razon_social
            or proveedor.nombre_completo
            or "",
        )

        if proveedor.retefuente_id:

            self.celda_retefuente._cargar_por_id(
                proveedor.retefuente_id,
            )

        else:

            self.celda_retefuente._seleccionar_vacio()

        if proveedor.reteica_id:

            self.celda_reteica._cargar_por_id(
                proveedor.reteica_id,
            )

        else:

            self.celda_reteica._seleccionar_vacio()

        if proveedor.reteiva_id:

            self.celda_reteiva._cargar_por_id(
                proveedor.reteiva_id,
            )

        else:

            self.celda_reteiva._seleccionar_vacio()

        self._recalcular_totales()

    def _agregar_fila(
        self,
        datos=None,
    ):

        fila = self.tabla.rowCount()

        self.tabla.insertRow(
            fila,
        )

        descripcion = QLineEdit()

        if datos:

            descripcion.setText(
                datos.get(
                    "descripcion",
                    "",
                ),
            )

        self.tabla.setCellWidget(
            fila,
            COL_DESCRIPCION,
            descripcion,
        )

        cantidad = QDoubleSpinBox()

        cantidad.setRange(
            0,
            999999999,
        )
        cantidad.setDecimals(
            2,
        )
        cantidad.setValue(
            float(
                datos.get(
                    "cantidad",
                    1,
                )
                if datos
                else 1
            ),
        )
        cantidad.valueChanged.connect(
            lambda _v, f=fila: self._recalcular_fila(
                f,
            ),
        )

        self.tabla.setCellWidget(
            fila,
            COL_CANTIDAD,
            cantidad,
        )

        precio = QDoubleSpinBox()

        precio.setRange(
            0,
            999999999999,
        )
        precio.setDecimals(
            2,
        )
        precio.setValue(
            float(
                datos.get(
                    "precio_unitario",
                    0,
                )
                if datos
                else 0
            ),
        )
        precio.valueChanged.connect(
            lambda _v, f=fila: self._recalcular_fila(
                f,
            ),
        )

        self.tabla.setCellWidget(
            fila,
            COL_PRECIO,
            precio,
        )

        impuesto = CeldaImpuestoIVA(
            datos.get(
                "impuesto_id",
            )
            if datos
            else None,
        )

        impuesto.combo.currentIndexChanged.connect(
            lambda _i, f=fila: self._recalcular_fila(
                f,
            ),
        )

        self.tabla.setCellWidget(
            fila,
            COL_IMPUESTO,
            impuesto,
        )

        total_item = QTableWidgetItem(
            "$ 0",
        )
        total_item.setFlags(
            total_item.flags()
            & ~Qt.ItemFlag.ItemIsEditable,
        )

        self.tabla.setItem(
            fila,
            COL_TOTAL,
            total_item,
        )

        btn_borrar = QPushButton(
            "✕",
        )
        btn_borrar.setFixedWidth(
            28,
        )
        btn_borrar.clicked.connect(
            lambda _c=False, f=fila: self._borrar_fila(
                f,
            ),
        )

        self.tabla.setCellWidget(
            fila,
            COL_BORRAR,
            btn_borrar,
        )

        for columna, widget in (
            (COL_DESCRIPCION, descripcion),
            (COL_CANTIDAD, cantidad),
            (COL_PRECIO, precio),
            (COL_IMPUESTO, impuesto),
        ):

            self._conectar_enter_avanza(
                widget,
                columna,
            )

        self._recalcular_fila(
            fila,
        )

    def _borrar_fila(
        self,
        fila: int,
    ):

        if (
            fila < 0
            or fila >= self.tabla.rowCount()
        ):

            return

        self.tabla.removeRow(
            fila,
        )

        self._recalcular_totales()

    def _widget_fila(
        self,
        fila: int,
        columna: int,
    ):

        return self.tabla.cellWidget(
            fila,
            columna,
        )

    _ORDEN_COLUMNAS_FILA = (
        COL_DESCRIPCION,
        COL_CANTIDAD,
        COL_PRECIO,
        COL_IMPUESTO,
    )

    @staticmethod
    def _enfocar_widget(
        widget: QWidget,
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
        widget: QWidget,
        columna: int,
    ) -> None:
        """
        Busca en qué fila está ``widget`` en este momento (no se
        guarda el índice al conectar la señal, porque agregar o
        borrar filas lo correría) y le pone foco al siguiente campo
        de la planilla: la próxima columna de la misma fila, o la
        descripción de la fila de abajo si ya era la última
        columna.
        """

        for fila in range(
            self.tabla.rowCount(),
        ):

            if (
                self._widget_fila(
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

                siguiente = self._widget_fila(
                    fila,
                    self._ORDEN_COLUMNAS_FILA[
                        indice + 1
                    ],
                )

            else:

                siguiente = self._widget_fila(
                    fila + 1,
                    COL_DESCRIPCION,
                )

            if siguiente is not None:

                self._enfocar_widget(
                    siguiente,
                )

            return

    def _conectar_enter_avanza(
        self,
        widget: QWidget,
        columna: int,
    ) -> None:
        """
        Enter en un campo de la tabla de ítems avanza al siguiente
        como en una planilla, en vez de no hacer nada. No usa el
        tab order de Qt (``focusNextChild``) porque ese orden es
        global al formulario y mezclarlo con el de la cabecera
        movía el foco a otro lado del que se esperaba.
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

        elif isinstance(
            widget,
            QLineEdit,
        ):

            widget.returnPressed.connect(
                manejador,
            )

    def _recalcular_fila(
        self,
        fila: int,
    ):

        cantidad = self._widget_fila(
            fila,
            COL_CANTIDAD,
        )
        precio = self._widget_fila(
            fila,
            COL_PRECIO,
        )
        impuesto = self._widget_fila(
            fila,
            COL_IMPUESTO,
        )

        if (
            cantidad is None
            or precio is None
            or impuesto is None
        ):

            return

        _, total = ServicioFacturaCompra._calcular_linea(
            cantidad.value(),
            precio.value(),
            impuesto.valor(),
        )

        item = self.tabla.item(
            fila,
            COL_TOTAL,
        )

        if item is not None:

            item.setText(
                f"$ {total:,.2f}",
            )

        self._recalcular_totales()

    def _recalcular_totales(
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
                self._recalcular_totales_ahora,
            )
            self._timer_totales = timer

        timer.start()

    def _recalcular_totales_ahora(
        self,
    ):

        lineas = self._obtener_lineas()

        cabecera = {
            "retefuente_id": self.celda_retefuente.valor(),
            "reteica_id": self.celda_reteica.valor(),
            "reteiva_id": self.celda_reteiva.valor(),
        }

        try:

            ServicioFacturaCompra._aplicar_resumen(
                cabecera,
                lineas,
            )

            subtotal = float(
                cabecera.get(
                    "subtotal",
                    0,
                )
                or 0,
            )
            iva = float(
                cabecera.get(
                    "iva",
                    0,
                )
                or 0,
            )
            total = float(
                cabecera.get(
                    "total",
                    0,
                )
                or 0,
            )

        except Exception:

            subtotal = iva = total = 0.0

        self.lbl_subtotal.setText(
            f"Subtotal: $ {subtotal:,.2f}",
        )
        self.lbl_iva.setText(
            f"IVA: $ {iva:,.2f}",
        )
        self.lbl_total.setText(
            f"Total: $ {total:,.2f}",
        )

    def _obtener_lineas(
        self,
    ) -> list[dict]:

        lineas = []

        for fila in range(
            self.tabla.rowCount(),
        ):

            descripcion = self._widget_fila(
                fila,
                COL_DESCRIPCION,
            )
            cantidad = self._widget_fila(
                fila,
                COL_CANTIDAD,
            )
            precio = self._widget_fila(
                fila,
                COL_PRECIO,
            )
            impuesto = self._widget_fila(
                fila,
                COL_IMPUESTO,
            )

            lineas.append(
                {
                    "descripcion": (
                        descripcion.text().strip()
                        if descripcion
                        else ""
                    ),
                    "cantidad": (
                        cantidad.value()
                        if cantidad
                        else 0
                    ),
                    "precio_unitario": (
                        precio.value()
                        if precio
                        else 0
                    ),
                    "impuesto_id": (
                        impuesto.valor()
                        if impuesto
                        else None
                    ),
                    "precio_incluye_iva": False,
                },
            )

        return lineas

    def _obtener_cabecera(
        self,
    ) -> dict:

        return {
            "numero": self.txt_numero.text().strip(),
            "fecha": self.fecha.date().toPython(),
            "proveedor_id": self.proveedor.valor(),
            "nit_proveedor": self.txt_nit.text().strip(),
            "razon_social_proveedor": (
                self.txt_razon.text().strip()
            ),
            "numero_proveedor": (
                self.txt_numero_proveedor.text().strip()
            ),
            "prefijo": self.txt_prefijo.text().strip(),
            "consecutivo": (
                self.txt_consecutivo.text().strip()
            ),
            "cufe": self.txt_cufe.text().strip(),
            "observaciones": (
                self.observaciones.toPlainText().strip()
            ),
            "retefuente_id": self.celda_retefuente.valor(),
            "reteica_id": self.celda_reteica.valor(),
            "reteiva_id": self.celda_reteiva.valor(),
            "formato_impresion": self.formato.currentData(),
            "origen": (
                "xml"
                if self._ruta_xml_pendiente
                else "manual"
            ),
            "ruta_xml": "",
            "estado": "recibida",
            "activo": True,
        }

    def _importar_xml(
        self,
    ):

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Importar factura electrónica",
            "",
            "XML (*.xml);;Todos (*.*)",
        )

        if not ruta:

            return

        try:

            datos = self.datasource.preparar_desde_xml(
                ruta,
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Importar XML",
                str(error),
            )

            return

        self._aplicar_datos_importados(
            datos,
            ruta,
        )

        QMessageBox.information(
            self,
            "Importar XML",
            "Datos cargados desde el XML. "
            "Revise y guarde la factura.",
        )

    def _aplicar_datos_importados(
        self,
        datos: dict,
        ruta_xml: str,
    ):

        cabecera = datos["cabecera"]

        self._ruta_xml_pendiente = ruta_xml

        self.txt_numero.setText(
            cabecera.get(
                "numero",
                self.txt_numero.text(),
            ),
        )

        fecha = cabecera.get(
            "fecha",
        ) or date.today()

        self.fecha.setDate(
            QDate(
                fecha.year,
                fecha.month,
                fecha.day,
            ),
        )

        if cabecera.get(
            "proveedor_id",
        ):

            self.proveedor.setValue(
                cabecera["proveedor_id"],
            )

        self.txt_nit.setText(
            cabecera.get(
                "nit_proveedor",
                "",
            ),
        )
        self.txt_razon.setText(
            cabecera.get(
                "razon_social_proveedor",
                "",
            ),
        )
        self.txt_numero_proveedor.setText(
            cabecera.get(
                "numero_proveedor",
                "",
            ),
        )
        self.txt_prefijo.setText(
            cabecera.get(
                "prefijo",
                "",
            ),
        )
        self.txt_consecutivo.setText(
            cabecera.get(
                "consecutivo",
                "",
            ),
        )
        self.txt_cufe.setText(
            cabecera.get(
                "cufe",
                "",
            ),
        )

        self.tabla.setRowCount(
            0,
        )

        for linea in datos.get(
            "lineas",
            [],
        ):

            self._agregar_fila(
                linea,
            )

        if self.tabla.rowCount() == 0:

            self._agregar_fila()

        self._recalcular_totales()

    def _cargar_datos(
        self,
    ):

        if self.id_registro is None:

            return

        factura = self.datasource.obtener_completa(
            self.id_registro,
        )

        if factura is None:

            return

        self.txt_numero.setText(
            factura.numero,
        )

        self.fecha.setDate(
            QDate(
                factura.fecha.year,
                factura.fecha.month,
                factura.fecha.day,
            ),
        )

        if factura.proveedor_id:

            self.proveedor.setValue(
                factura.proveedor_id,
            )

        self.txt_nit.setText(
            factura.nit_proveedor
            or "",
        )
        self.txt_razon.setText(
            factura.razon_social_proveedor
            or "",
        )
        self.txt_numero_proveedor.setText(
            factura.numero_proveedor
            or "",
        )
        self.txt_prefijo.setText(
            factura.prefijo
            or "",
        )
        self.txt_consecutivo.setText(
            factura.consecutivo
            or "",
        )
        self.txt_cufe.setText(
            factura.cufe
            or "",
        )
        self.observaciones.setPlainText(
            factura.observaciones
            or "",
        )

        if factura.formato_impresion:

            indice_formato = self.formato.findData(
                factura.formato_impresion,
            )

            if indice_formato >= 0:

                self.formato.setCurrentIndex(
                    indice_formato,
                )

        if factura.retefuente_id:

            self.celda_retefuente._cargar_por_id(
                factura.retefuente_id,
            )

        else:

            self.celda_retefuente._seleccionar_vacio()

        if factura.reteica_id:

            self.celda_reteica._cargar_por_id(
                factura.reteica_id,
            )

        else:

            self.celda_reteica._seleccionar_vacio()

        if factura.reteiva_id:

            self.celda_reteiva._cargar_por_id(
                factura.reteiva_id,
            )

        else:

            self.celda_reteiva._seleccionar_vacio()

        self.tabla.setRowCount(
            0,
        )

        for detalle in factura.detalles:

            self._agregar_fila(
                {
                    "descripcion": detalle.descripcion,
                    "cantidad": detalle.cantidad,
                    "precio_unitario": (
                        detalle.precio_unitario
                    ),
                    "impuesto_id": detalle.impuesto_id,
                },
            )

        self._recalcular_totales()

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
            if not FormularioFacturaCompra._linea_vacia(
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

    def guardar(
        self,
    ):

        cabecera = self._obtener_cabecera()
        lineas = self._lineas_no_vacias(
            self._obtener_lineas(),
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

            if (
                self._ruta_xml_pendiente
                and not self.es_edicion
            ):

                from aplicacion.integraciones.dian.importador_xml import (
                    copiar_xml_almacen,
                )

                cabecera["ruta_xml"] = copiar_xml_almacen(
                    self._ruta_xml_pendiente,
                    carpeta_destino=(
                        ServicioFacturaCompra.carpeta_xml()
                    ),
                    cufe=cabecera.get(
                        "cufe",
                        "",
                    ),
                )

            factura = self.datasource.guardar_completa(
                cabecera,
                lineas,
                self.id_registro,
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                str(error),
            )

            return

        self.id_registro = factura.id
        self.es_edicion = True
        self._ruta_xml_pendiente = ""

        self.txt_numero.setText(
            factura.numero,
        )

        QMessageBox.information(
            self,
            "Información",
            "Factura de compra guardada correctamente.",
        )

        self.guardado.emit()
