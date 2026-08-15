from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, Qt, Signal
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

    def guardar(
        self,
    ):

        try:

            cabecera = self._obtener_cabecera()

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
                self._obtener_lineas(),
                self.id_registro,
            )

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

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                str(error),
            )
