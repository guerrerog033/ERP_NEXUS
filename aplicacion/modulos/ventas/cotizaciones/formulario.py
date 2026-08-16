from __future__ import annotations

from datetime import date

from shiboken6 import isValid

from PySide6.QtCore import (
    QEvent,
    QObject,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QDoubleSpinBox,
)

from aplicacion.framework.base.page import Page
from aplicacion.framework.app_context import AppContext
from aplicacion.framework.lookup import (
    LookupWidget,
)
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
from aplicacion.maestros.impuestos.servicios import (
    ServicioImpuesto,
)
from aplicacion.maestros.productos.producto_lookup_dialog import (
    ProductoLookupDialog,
)
from aplicacion.maestros.productos.imagen_producto import (
    ImagenProductoLabel,
)
from aplicacion.maestros.productos.servicios import (
    ServicioProducto,
)
from aplicacion.maestros.productos.precio_volumen_servicio import (
    ServicioPrecioVolumenProducto,
)
from aplicacion.maestros.terceros.cliente_lookup import (
    ClienteLookup,
)
from aplicacion.maestros.terceros.servicio import (
    TerceroServicio,
)
from aplicacion.modulos.ventas.cotizaciones.cotizacion_definition import (
    CotizacionDefinition,
)
from aplicacion.modulos.ventas.cotizaciones.datasource import (
    CotizacionDataSource,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    formatos_combo,
    normalizar_formato_codigo,
)
from aplicacion.modulos.ventas.cotizaciones.impresion import (
    enviar_correo_cotizacion,
    enviar_whatsapp_cotizacion,
    exportar_pdf_cotizacion,
    imprimir_cotizacion,
)
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)
from aplicacion.recursos.ui.botones import Botones


COL_IMAGEN = 0
COL_CODIGO = 1
COL_PRODUCTO = 2
COL_CANTIDAD = 3
COL_PRECIO = 4
COL_IMPUESTO = 5
COL_TOTAL = 6
COL_BORRAR = 7

ANCHO_MINIMO_TABLA = 860
ALTURA_FILA_TABLA = 64


class _FiltroEdicionTabla(
    QObject,
):

    def __init__(
        self,
        tabla: QTableWidget,
    ):

        super().__init__(
            tabla,
        )

        self._tabla = tabla

    def _widget_interactivo_en(
        self,
        widget: QWidget | None,
        posicion_local,
    ) -> QWidget | None:

        if widget is None:

            return None

        candidato = widget.childAt(
            posicion_local,
        )

        if candidato is not None:

            while candidato is not None:

                if isinstance(
                    candidato,
                    (
                        QDoubleSpinBox,
                        QComboBox,
                        QPushButton,
                    ),
                ):

                    return candidato

                candidato = candidato.parentWidget()

        if isinstance(
            widget,
            (
                QDoubleSpinBox,
                QComboBox,
                QPushButton,
            ),
        ):

            return widget

        return None

    def eventFilter(
        self,
        watched,
        event,
    ):

        if not isValid(
            self._tabla,
        ):

            return False

        if (
            watched is self._tabla.viewport()
            and event.type()
            == QEvent.Type.MouseButtonPress
        ):

            posicion = event.position().toPoint()

            indice = self._tabla.indexAt(
                posicion,
            )

            if indice.isValid():

                celda = self._tabla.cellWidget(
                    indice.row(),
                    indice.column(),
                )

                if celda is not None:

                    posicion_local = celda.mapFrom(
                        self._tabla.viewport(),
                        posicion,
                    )

                    objetivo = self._widget_interactivo_en(
                        celda,
                        posicion_local,
                    )

                    if objetivo is not None:

                        if isinstance(
                            objetivo,
                            QPushButton,
                        ):

                            objetivo.click()

                        else:

                            objetivo.setFocus(
                                Qt.FocusReason.MouseFocusReason,
                            )

                            editor = getattr(
                                objetivo,
                                "lineEdit",
                                lambda: None,
                            )()

                            if editor is not None:

                                editor.setFocus(
                                    Qt.FocusReason.MouseFocusReason,
                                )

                    elif hasattr(
                        celda,
                        "etiqueta",
                    ):

                        handler = getattr(
                            celda,
                            "_abrir_producto",
                            None,
                        )

                        if callable(
                            handler,
                        ):

                            handler()

        return super().eventFilter(
            watched,
            event,
        )


class FormularioCotizacion(Page):

    guardado = Signal()

    cerrar = Signal()

    definition = CotizacionDefinition

    titulo = "Cotización"

    ancho = 1380

    alto = 680

    def __init__(
        self,
        id_registro=None,
        parent=None,
    ):

        self.id_registro = id_registro

        self.es_edicion = (
            id_registro is not None
        )

        self.datasource = CotizacionDataSource()

        self._cargando_registro = False

        ServicioImpuesto.inicializar_predeterminados()

        super().__init__(
            parent,
        )

    def _crear_ui(self):

        super()._crear_ui()

        self.layout_principal.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.card = Card(
            "",
        )

        self.layout_principal.addWidget(
            self.card,
        )

        cabecera = QWidget()

        self.txt_numero = QLabel(
            ServicioCotizacion.generar_numero(),
        )

        self.fecha = QDateEdit()

        self.fecha.setCalendarPopup(
            True,
        )

        self.fecha.setDate(
            date.today(),
        )

        self.cliente = LookupWidget(
            ClienteLookup(),
        )

        self.cliente.seleccionado.connect(
            self._aplicar_retenciones_cliente,
        )

        self.formato = QComboBox()

        for etiqueta, codigo in formatos_combo():

            self.formato.addItem(
                etiqueta,
                codigo,
            )

        indice = self.formato.findData(
            ServicioCotizacion.formato_predeterminado(),
        )

        if indice >= 0:

            self.formato.setCurrentIndex(
                indice,
            )

        self.observaciones = QTextEdit()

        self.vendedor = QLineEdit()

        if (
            not self.es_edicion
            and AppContext.usuario is not None
        ):

            self.vendedor.setText(
                AppContext.usuario.nombre,
            )

        grid = QGridLayout(
            cabecera,
        )

        grid.setContentsMargins(
            16,
            8,
            16,
            8,
        )

        grid.setHorizontalSpacing(
            16,
        )

        grid.setVerticalSpacing(
            8,
        )

        etiqueta_numero = QLabel(
            "Número",
        )

        etiqueta_fecha = QLabel(
            "Fecha",
        )

        etiqueta_cliente = QLabel(
            "Cliente",
        )

        etiqueta_formato = QLabel(
            "Formato impresión",
        )

        etiqueta_vendedor = QLabel(
            "Vendedor",
        )

        self.fecha.setMaximumWidth(
            170,
        )

        self.formato.setMaximumWidth(
            170,
        )

        grid.addWidget(
            etiqueta_numero,
            0,
            0,
        )

        grid.addWidget(
            self.txt_numero,
            0,
            1,
        )

        grid.addWidget(
            etiqueta_fecha,
            0,
            2,
        )

        grid.addWidget(
            self.fecha,
            0,
            3,
        )

        grid.addWidget(
            etiqueta_cliente,
            1,
            0,
        )

        grid.addWidget(
            self.cliente,
            1,
            1,
            1,
            3,
        )

        grid.addWidget(
            etiqueta_formato,
            2,
            0,
        )

        grid.addWidget(
            self.formato,
            2,
            1,
        )

        grid.addWidget(
            etiqueta_vendedor,
            2,
            2,
        )

        grid.addWidget(
            self.vendedor,
            2,
            3,
        )

        grid.setColumnStretch(
            1,
            1,
        )

        grid.setColumnStretch(
            3,
            2,
        )

        self.card.agregar_widget(
            cabecera,
        )

        self.tabla = QTableWidget(
            0,
            8,
        )

        self._configurar_tabla_lineas()

        self.scroll_tabla = QScrollArea()

        self.scroll_tabla.setWidgetResizable(
            True,
        )

        self.scroll_tabla.setFrameShape(
            QFrame.Shape.NoFrame,
        )

        self.scroll_tabla.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        )

        self.scroll_tabla.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        )

        self.scroll_tabla.setMinimumHeight(
            240,
        )

        self.contenedor_tabla = QWidget()

        layout_contenedor_tabla = QVBoxLayout(
            self.contenedor_tabla,
        )

        layout_contenedor_tabla.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.tabla.setMinimumWidth(
            ANCHO_MINIMO_TABLA,
        )

        self.tabla.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout_contenedor_tabla.addWidget(
            self.tabla,
        )

        self.scroll_tabla.setWidget(
            self.contenedor_tabla,
        )

        self.scroll_tabla.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.card.agregar_widget(
            self.scroll_tabla,
        )

        panel_observaciones = QWidget()

        layout_observaciones = QVBoxLayout(
            panel_observaciones,
        )

        layout_observaciones.setContentsMargins(
            16,
            0,
            8,
            0,
        )

        layout_observaciones.setSpacing(
            4,
        )

        etiqueta_observaciones = QLabel(
            "Observaciones",
        )

        self.observaciones.setMinimumHeight(
            120,
        )

        layout_observaciones.addWidget(
            etiqueta_observaciones,
        )

        layout_observaciones.addWidget(
            self.observaciones,
            1,
        )

        acciones_lineas = QHBoxLayout()

        self.btn_agregar_linea = Botones.nuevo()

        self.btn_agregar_linea.setText(
            "Agregar línea",
        )

        acciones_lineas.addWidget(
            self.btn_agregar_linea,
        )

        acciones_lineas.addWidget(
            panel_observaciones,
            1,
        )

        panel_totales = QWidget()

        panel_totales.setMinimumWidth(
            360,
        )

        layout_totales = QVBoxLayout(
            panel_totales,
        )

        layout_totales.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout_totales.setSpacing(
            6,
        )

        fila_subtotal = QHBoxLayout()

        fila_subtotal.addStretch()

        self.lbl_subtotal = QLabel(
            "Subtotal: $ 0,00",
        )

        self.lbl_subtotal.setMinimumWidth(
            180,
        )

        self.lbl_subtotal.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter,
        )

        fila_subtotal.addWidget(
            self.lbl_subtotal,
        )

        layout_totales.addLayout(
            fila_subtotal,
        )

        fila_retefuente = QHBoxLayout()

        fila_retefuente.addStretch()

        etiqueta_retefuente = QLabel(
            "Retefuente:",
        )

        self.celda_retefuente = CeldaRetencionCombo(
            lookup=RetefuenteLookup(),
        )

        self.celda_retefuente.setMinimumWidth(
            170,
        )

        self._conectar_recalculo_retencion(
            self.celda_retefuente,
        )

        self.lbl_valor_retefuente = QLabel(
            "$ 0,00",
        )

        self.lbl_valor_retefuente.setMinimumWidth(
            70,
        )

        self.lbl_valor_retefuente.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter,
        )

        fila_retefuente.addWidget(
            etiqueta_retefuente,
        )

        fila_retefuente.addWidget(
            self.celda_retefuente,
        )

        fila_retefuente.addWidget(
            self.lbl_valor_retefuente,
        )

        layout_totales.addLayout(
            fila_retefuente,
        )

        fila_reteica = QHBoxLayout()

        fila_reteica.addStretch()

        etiqueta_reteica = QLabel(
            "ReteICA:",
        )

        self.celda_reteica = CeldaRetencionCombo(
            lookup=ReteICALookup(),
        )

        self.celda_reteica.setMinimumWidth(
            170,
        )

        self._conectar_recalculo_retencion(
            self.celda_reteica,
        )

        self.lbl_valor_reteica = QLabel(
            "$ 0,00",
        )

        self.lbl_valor_reteica.setMinimumWidth(
            70,
        )

        self.lbl_valor_reteica.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter,
        )

        fila_reteica.addWidget(
            etiqueta_reteica,
        )

        fila_reteica.addWidget(
            self.celda_reteica,
        )

        fila_reteica.addWidget(
            self.lbl_valor_reteica,
        )

        layout_totales.addLayout(
            fila_reteica,
        )

        fila_reteiva = QHBoxLayout()

        fila_reteiva.addStretch()

        etiqueta_reteiva = QLabel(
            "ReteIVA:",
        )

        self.celda_reteiva = CeldaRetencionCombo(
            lookup=ReteIVALookup(),
        )

        self.celda_reteiva.setMinimumWidth(
            170,
        )

        self._conectar_recalculo_retencion(
            self.celda_reteiva,
        )

        self.lbl_valor_reteiva = QLabel(
            "$ 0,00",
        )

        self.lbl_valor_reteiva.setMinimumWidth(
            70,
        )

        self.lbl_valor_reteiva.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter,
        )

        fila_reteiva.addWidget(
            etiqueta_reteiva,
        )

        fila_reteiva.addWidget(
            self.celda_reteiva,
        )

        fila_reteiva.addWidget(
            self.lbl_valor_reteiva,
        )

        layout_totales.addLayout(
            fila_reteiva,
        )

        fila_total = QHBoxLayout()

        fila_total.addStretch()

        self.lbl_total = QLabel(
            "Total: $ 0,00",
        )

        self.lbl_total.setMinimumWidth(
            180,
        )

        self.lbl_total.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter,
        )

        fuente_total = self.lbl_total.font()

        fuente_total.setBold(
            True,
        )

        self.lbl_total.setFont(
            fuente_total,
        )

        fila_total.addWidget(
            self.lbl_total,
        )

        layout_totales.addLayout(
            fila_total,
        )

        acciones_lineas.addWidget(
            panel_totales,
        )

        self.card.agregar_layout(
            acciones_lineas,
        )

        botones = QHBoxLayout()

        botones.addStretch()

        self.btn_imprimir = Botones.editar()

        self.btn_imprimir.setText(
            "Imprimir",
        )

        self.btn_pdf = Botones.aceptar()

        self.btn_pdf.setText(
            "PDF",
        )

        self.btn_whatsapp = Botones.nuevo()

        self.btn_whatsapp.setText(
            "WhatsApp",
        )

        self.btn_correo = Botones.buscar()

        self.btn_correo.setText(
            "Correo",
        )

        self.btn_guardar = Botones.guardar()

        self.btn_cancelar = Botones.cancelar()

        botones.addWidget(
            self.btn_imprimir,
        )

        botones.addWidget(
            self.btn_pdf,
        )

        botones.addWidget(
            self.btn_whatsapp,
        )

        botones.addWidget(
            self.btn_correo,
        )

        botones.addWidget(
            self.btn_guardar,
        )

        botones.addWidget(
            self.btn_cancelar,
        )

        self.card.agregar_layout(
            botones,
        )

        self.btn_agregar_linea.clicked.connect(
            self._agregar_linea,
        )

        self.btn_guardar.clicked.connect(
            self.guardar,
        )

        self.btn_cancelar.clicked.connect(
            self.cerrar.emit,
        )

        self.btn_imprimir.clicked.connect(
            self.imprimir,
        )

        self.btn_pdf.clicked.connect(
            self.exportar_pdf,
        )

        self.btn_whatsapp.clicked.connect(
            self.enviar_whatsapp,
        )

        self.btn_correo.clicked.connect(
            self.enviar_correo,
        )

        if self.es_edicion:

            self._cargar_registro()

        else:

            self._agregar_linea()

    def _cargar_registro(self):

        cotizacion = self.datasource.obtener_completa(
            self.id_registro,
        )

        if cotizacion is None:

            return

        self._cargando_registro = True

        self.txt_numero.setText(
            cotizacion.numero,
        )

        self.fecha.setDate(
            cotizacion.fecha,
        )

        self.cliente.setValue(
            cotizacion.cliente_id,
        )

        indice = self.formato.findData(
            normalizar_formato_codigo(
                cotizacion.formato_impresion,
            ),
        )

        if indice >= 0:

            self.formato.setCurrentIndex(
                indice,
            )

        self.observaciones.setPlainText(
            cotizacion.observaciones
            or "",
        )

        self.vendedor.setText(
            getattr(
                cotizacion,
                "vendedor",
                "",
            )
            or "",
        )

        if cotizacion.retefuente_id:

            self.celda_retefuente._cargar_por_id(
                cotizacion.retefuente_id,
            )

        else:

            self.celda_retefuente._seleccionar_vacio()

        if cotizacion.reteica_id:

            self.celda_reteica._cargar_por_id(
                cotizacion.reteica_id,
            )

        else:

            self.celda_reteica._seleccionar_vacio()

        if getattr(
            cotizacion,
            "reteiva_id",
            None,
        ):

            self.celda_reteiva._cargar_por_id(
                cotizacion.reteiva_id,
            )

        else:

            self.celda_reteiva._seleccionar_vacio()

        self._cargando_registro = False

        self.tabla.setRowCount(
            0,
        )

        for detalle in cotizacion.detalles:

            producto = None
            item = None
            producto_variante_id = getattr(
                detalle,
                "producto_variante_id",
                None,
            )

            if detalle.producto_id:

                if producto_variante_id:

                    item = ServicioProducto.resolver_item(
                        detalle.producto_id,
                        producto_variante_id,
                    )

                    producto = item["producto"]

                else:

                    producto = ServicioProducto.obtener_por_id(
                        detalle.producto_id,
                    )

            imagen = None

            if producto is not None:

                ruta_imagen = (
                    ServicioProducto.resolver_imagen_item(
                        producto,
                        item["variante"]
                        if item is not None
                        else None,
                    )
                )

                if ruta_imagen is not None:

                    imagen = str(
                        ruta_imagen,
                    )

            codigo = ""
            nombre = detalle.descripcion or ""

            if (
                detalle.producto_id
                and producto_variante_id
            ):

                codigo = item["codigo"]
                nombre = item["nombre"]

            elif producto is not None:

                codigo = producto.codigo or ""
                nombre = producto.nombre or nombre

            elif " - " in nombre:

                partes = nombre.split(
                    " - ",
                    1,
                )

                codigo = partes[0]
                nombre = partes[1]

            precio_incluye_iva = bool(
                getattr(
                    detalle,
                    "precio_incluye_iva",
                    False,
                )
            )

            if (
                producto is not None
                and not precio_incluye_iva
            ):

                precio_incluye_iva = bool(
                    producto.precio_incluye_iva,
                )

            self._agregar_linea(
                producto_id=detalle.producto_id,
                producto_variante_id=(
                    producto_variante_id
                ),
                codigo=codigo,
                nombre=nombre,
                cantidad=detalle.cantidad,
                precio=detalle.precio_unitario,
                impuesto_id=detalle.impuesto_id,
                precio_incluye_iva=precio_incluye_iva,
                imagen=imagen,
            )

        self._recalcular_totales()

    def _configurar_tabla_lineas(self):

        self.tabla.setHorizontalHeaderLabels(
            [
                "Imagen",
                "Código",
                "Producto",
                "Cantidad",
                "Precio",
                "Impuesto",
                "Total",
                "",
            ],
        )

        self.tabla.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers,
        )

        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectItems,
        )

        self.tabla.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection,
        )

        self.tabla.setFocusPolicy(
            Qt.FocusPolicy.ClickFocus,
        )

        self.tabla.setHorizontalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel,
        )

        self.tabla.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )

        self.tabla.setMinimumWidth(
            ANCHO_MINIMO_TABLA,
        )

        self.tabla.verticalHeader().setDefaultSectionSize(
            ALTURA_FILA_TABLA,
        )

        self.tabla.horizontalHeader().setMinimumSectionSize(
            44,
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_IMAGEN,
            QHeaderView.ResizeMode.Fixed,
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_CODIGO,
            QHeaderView.ResizeMode.Fixed,
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_PRODUCTO,
            QHeaderView.ResizeMode.Stretch,
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_CANTIDAD,
            QHeaderView.ResizeMode.Fixed,
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_PRECIO,
            QHeaderView.ResizeMode.Fixed,
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_IMPUESTO,
            QHeaderView.ResizeMode.Fixed,
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_TOTAL,
            QHeaderView.ResizeMode.Fixed,
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_BORRAR,
            QHeaderView.ResizeMode.Fixed,
        )

        self.tabla.setColumnWidth(
            COL_IMAGEN,
            72,
        )

        self.tabla.setColumnWidth(
            COL_CODIGO,
            100,
        )

        self.tabla.setColumnWidth(
            COL_CANTIDAD,
            92,
        )

        self.tabla.setColumnWidth(
            COL_PRECIO,
            105,
        )

        self.tabla.setColumnWidth(
            COL_IMPUESTO,
            118,
        )

        self.tabla.setColumnWidth(
            COL_TOTAL,
            95,
        )

        self.tabla.setColumnWidth(
            COL_BORRAR,
            44,
        )

        self.tabla.setStyleSheet(
            """
            QTableWidget {
                background: white;
                gridline-color: #C8D8E8;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget QWidget {
                background-color: transparent;
            }
            QDoubleSpinBox,
            QLineEdit,
            QComboBox {
                background: white;
                color: #1F2937;
                border: 1px solid #B0C4D8;
                border-radius: 4px;
                padding: 4px;
                min-height: 28px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #4A7FB0;
            }
            QLineEdit:focus {
                border: 2px solid #4A7FB0;
            }
            QComboBox:focus {
                border: 2px solid #4A7FB0;
            }
            QDoubleSpinBox::up-button,
            QDoubleSpinBox::down-button {
                width: 18px;
                subcontrol-origin: border;
            }
            """,
        )

        self._filtro_tabla = _FiltroEdicionTabla(
            self.tabla,
        )

        self.tabla.viewport().installEventFilter(
            self._filtro_tabla,
        )

    def _limpiar_items_fila(
        self,
        fila: int,
    ):

        for columna in range(
            self.tabla.columnCount(),
        ):

            self.tabla.removeCellWidget(
                fila,
                columna,
            )

            self.tabla.takeItem(
                fila,
                columna,
            )

    def _envolver_widget_celda(
        self,
        widget: QWidget,
    ) -> QWidget:

        contenedor = QWidget()

        contenedor.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        contenedor.setMinimumHeight(
            ALTURA_FILA_TABLA - 8,
        )

        layout = QVBoxLayout(
            contenedor,
        )

        layout.setContentsMargins(
            2,
            4,
            2,
            4,
        )

        layout.setSpacing(
            0,
        )

        widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        widget.setMinimumHeight(
            32,
        )

        layout.addWidget(
            widget,
        )

        return contenedor

    def _asignar_celda(
        self,
        fila: int,
        columna: int,
        widget: QWidget,
        *,
        envolver: bool = False,
    ) -> None:

        if envolver:

            widget = self._envolver_widget_celda(
                widget,
            )

        self.tabla.setCellWidget(
            fila,
            columna,
            widget,
        )

        self.tabla.takeItem(
            fila,
            columna,
        )

    def _impuesto_iva_predeterminado_id(
        self,
    ):

        from aplicacion.maestros.impuestos.iva_catalogo import (
            id_iva_predeterminado,
        )

        return id_iva_predeterminado()

    def _crear_spin_decimal(
        self,
        valor: float,
        minimo: float,
        maximo: float,
        decimales: int = 2,
    ) -> QDoubleSpinBox:

        spin = QDoubleSpinBox()

        spin.setRange(
            minimo,
            maximo,
        )

        spin.setDecimals(
            decimales,
        )

        spin.setMinimumWidth(
            75,
        )

        spin.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus,
        )

        spin.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.UpDownArrows,
        )

        spin.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter,
        )

        spin.setKeyboardTracking(
            True,
        )

        spin.setValue(
            float(
                valor
                or 0,
            ),
        )

        editor = spin.lineEdit()

        if editor is not None:

            editor.setFocusPolicy(
                Qt.FocusPolicy.StrongFocus,
            )

        spin.valueChanged.connect(
            lambda _valor: self._recalcular_totales(),
        )

        return spin

    def _widget_celda(
        self,
        fila: int,
        columna: int,
    ):

        celda = self.tabla.cellWidget(
            fila,
            columna,
        )

        if celda is None:

            return None

        if isinstance(
            celda,
            QDoubleSpinBox,
        ):

            return celda

        layout = celda.layout()

        if (
            layout is not None
            and layout.count() > 0
        ):

            for indice in range(
                layout.count(),
            ):

                item = layout.itemAt(
                    indice,
                )

                if item is None:

                    continue

                widget = item.widget()

                if isinstance(
                    widget,
                    QDoubleSpinBox,
                ):

                    return widget

        return celda

    def _celda_impuesto_fila(
        self,
        fila: int,
    ):

        celda = self.tabla.cellWidget(
            fila,
            COL_IMPUESTO,
        )

        if celda is None:

            return None

        if hasattr(
            celda,
            "valor",
        ):

            return celda

        layout = celda.layout()

        if (
            layout is not None
            and layout.count() > 0
        ):

            widget = layout.itemAt(
                0,
            ).widget()

            if hasattr(
                widget,
                "valor",
            ):

                return widget

        return None

    def _crear_celda_codigo(
        self,
        codigo: str = "",
        producto_id=None,
        producto_variante_id=None,
    ) -> QWidget:

        contenedor = QWidget()

        contenedor.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        contenedor.setMinimumHeight(
            ALTURA_FILA_TABLA - 8,
        )

        layout = QHBoxLayout(
            contenedor,
        )

        layout.setContentsMargins(
            4,
            4,
            4,
            4,
        )

        etiqueta = QLabel(
            codigo,
        )

        etiqueta.setWordWrap(
            True,
        )

        etiqueta.setStyleSheet(
            "color: #1F2937;",
        )

        layout.addWidget(
            etiqueta,
        )

        contenedor.etiqueta = etiqueta
        contenedor.producto_id = producto_id
        contenedor.producto_variante_id = (
            producto_variante_id
        )

        return contenedor

    def _crear_celda_producto(
        self,
        nombre: str = "",
        producto_id=None,
        precio_incluye_iva=False,
        producto_variante_id=None,
    ) -> QWidget:

        contenedor = QWidget()

        contenedor.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        contenedor.setMinimumHeight(
            ALTURA_FILA_TABLA - 8,
        )

        layout = QHBoxLayout(
            contenedor,
        )

        layout.setContentsMargins(
            4,
            4,
            4,
            4,
        )

        etiqueta = QLabel(
            nombre
            or "Seleccione producto",
        )

        etiqueta.setWordWrap(
            True,
        )

        etiqueta.setStyleSheet(
            "color: #546E7A;",
        )

        etiqueta.setCursor(
            Qt.CursorShape.PointingHandCursor,
        )

        btn_buscar = Botones.buscar()

        btn_buscar.setText(
            "",
        )

        btn_buscar.setToolTip(
            "Buscar producto",
        )

        btn_buscar.setFixedSize(
            36,
            36,
        )

        layout.addWidget(
            etiqueta,
            1,
        )

        layout.addWidget(
            btn_buscar,
        )

        contenedor.etiqueta = etiqueta
        contenedor.producto_id = producto_id
        contenedor.producto_variante_id = (
            producto_variante_id
        )
        contenedor.precio_incluye_iva = precio_incluye_iva

        contenedor._abrir_producto = (
            lambda celda=contenedor: self._buscar_producto_celda(
                celda,
            )
        )

        btn_buscar.clicked.connect(
            lambda _checked=False,
            celda=contenedor: self._buscar_producto_celda(
                celda,
            ),
        )

        etiqueta.mousePressEvent = (
            lambda _event,
            celda=contenedor: self._buscar_producto_celda(
                celda,
            )
        )

        return contenedor

    def _conectar_recalculo_retencion(
        self,
        celda: CeldaRetencionCombo,
    ):

        celda.combo.currentIndexChanged.connect(
            lambda _indice: self._recalcular_totales(),
        )

    def _aplicar_retenciones_cliente(
        self,
        resultado,
    ):

        if self._cargando_registro:

            return

        if resultado is None:

            self.celda_retefuente._seleccionar_vacio()
            self.celda_reteica._seleccionar_vacio()
            self.celda_reteiva._seleccionar_vacio()
            self._recalcular_totales()

            return

        cliente = TerceroServicio.obtener_por_id(
            resultado.valor,
        )

        if cliente is None:

            return

        if cliente.retefuente_id:

            self.celda_retefuente._cargar_por_id(
                cliente.retefuente_id,
            )

        else:

            self.celda_retefuente._seleccionar_vacio()

        if cliente.reteica_id:

            self.celda_reteica._cargar_por_id(
                cliente.reteica_id,
            )

        else:

            self.celda_reteica._seleccionar_vacio()

        if cliente.reteiva_id:

            self.celda_reteiva._cargar_por_id(
                cliente.reteiva_id,
            )

        elif getattr(
            cliente,
            "resp_o23",
            False,
        ):

            self.celda_reteiva._cargar_por_codigo(
                "RIVA15",
            )

        else:

            self.celda_reteiva._seleccionar_vacio()

        self._recalcular_totales()

    def _conectar_recalculo_iva(
        self,
        celda: CeldaImpuestoIVA,
    ):

        celda.combo.currentIndexChanged.connect(
            lambda _indice: self._recalcular_totales(),
        )

    def _crear_celda_borrar(self) -> QWidget:

        contenedor = QWidget()

        layout = QHBoxLayout(
            contenedor,
        )

        layout.setContentsMargins(
            4,
            4,
            4,
            4,
        )

        btn = Botones.eliminar()

        btn.setText(
            "",
        )

        btn.setFixedSize(
            36,
            36,
        )

        btn.setToolTip(
            "Quitar línea",
        )

        layout.addWidget(
            btn,
        )

        btn.clicked.connect(
            lambda _checked=False,
            celda=contenedor: self._quitar_fila_celda(
                celda,
            ),
        )

        return contenedor

    def _quitar_fila_celda(
        self,
        celda: QWidget,
    ):

        for fila in range(
            self.tabla.rowCount(),
        ):

            if self.tabla.cellWidget(
                fila,
                COL_BORRAR,
            ) is celda:

                self.tabla.removeRow(
                    fila,
                )

                self._recalcular_totales()

                return

    def _crear_contenedor_imagen(
        self,
        producto=None,
        imagen=None,
        codigo: str = "",
    ) -> QWidget:

        contenedor = QWidget()

        contenedor.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout = QHBoxLayout(
            contenedor,
        )

        layout.setContentsMargins(
            2,
            2,
            2,
            2,
        )

        layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )

        label = ImagenProductoLabel()

        if producto is not None:

            label.establecer_producto(
                producto,
            )

        elif imagen or codigo:

            label.establecer_ruta_relativa(
                imagen,
                codigo=codigo
                or None,
            )

        layout.addWidget(
            label,
        )

        contenedor.imagen_label = label

        return contenedor

    def _actualizar_imagen_fila(
        self,
        fila: int,
        producto=None,
        imagen=None,
        codigo: str = "",
        variante=None,
    ) -> None:

        celda = self.tabla.cellWidget(
            fila,
            COL_IMAGEN,
        )

        label = getattr(
            celda,
            "imagen_label",
            None,
        )

        if not isinstance(
            label,
            ImagenProductoLabel,
        ):

            if isinstance(
                celda,
                ImagenProductoLabel,
            ):

                label = celda

            else:

                return

        if producto is not None:

            ruta = ServicioProducto.resolver_imagen_item(
                producto,
                variante,
            )

            label.establecer_ruta(
                ruta,
            )

            return

        label.establecer_ruta_relativa(
            imagen,
            codigo=codigo
            or None,
        )

    def _agregar_linea(
        self,
        producto_id=None,
        producto_variante_id=None,
        codigo="",
        nombre="",
        cantidad=1.0,
        precio=0.0,
        impuesto_id=None,
        precio_incluye_iva=False,
        imagen=None,
    ):

        fila = self.tabla.rowCount()

        self.tabla.insertRow(
            fila,
        )

        self._limpiar_items_fila(
            fila,
        )

        if (
            impuesto_id is None
            and producto_id is None
        ):

            impuesto_id = self._impuesto_iva_predeterminado_id()

        producto = None

        if producto_id is not None:

            producto = ServicioProducto.obtener_por_id(
                producto_id,
            )

        lbl_imagen = self._crear_contenedor_imagen(
            producto=producto,
            imagen=imagen,
            codigo=codigo,
        )

        self._asignar_celda(
            fila,
            COL_IMAGEN,
            lbl_imagen,
        )

        celda_codigo = self._crear_celda_codigo(
            codigo,
            producto_id,
            producto_variante_id,
        )

        self._asignar_celda(
            fila,
            COL_CODIGO,
            celda_codigo,
        )

        celda_producto = self._crear_celda_producto(
            nombre,
            producto_id,
            precio_incluye_iva,
            producto_variante_id,
        )

        self._asignar_celda(
            fila,
            COL_PRODUCTO,
            celda_producto,
        )

        spin_cantidad = self._crear_spin_decimal(
            float(
                cantidad
                or 1,
            ),
            0.01,
            999999,
        )

        self._asignar_celda(
            fila,
            COL_CANTIDAD,
            spin_cantidad,
            envolver=True,
        )

        spin_cantidad.valueChanged.connect(
            lambda _valor, f=fila: self._aplicar_precio_volumen(
                f,
            ),
        )

        spin_precio = self._crear_spin_decimal(
            float(
                precio
                or 0,
            ),
            0,
            999999999,
        )

        self._asignar_celda(
            fila,
            COL_PRECIO,
            spin_precio,
            envolver=True,
        )

        celda_impuesto = CeldaImpuestoIVA(
            impuesto_id=impuesto_id,
        )

        self._conectar_recalculo_iva(
            celda_impuesto,
        )

        self._asignar_celda(
            fila,
            COL_IMPUESTO,
            celda_impuesto,
            envolver=True,
        )

        item_total = QTableWidgetItem(
            "0,00",
        )

        item_total.setFlags(
            item_total.flags()
            & ~Qt.ItemIsEditable,
        )

        item_total.setTextAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter,
        )

        self.tabla.setItem(
            fila,
            COL_TOTAL,
            item_total,
        )

        self.tabla.setCellWidget(
            fila,
            COL_BORRAR,
            self._crear_celda_borrar(),
        )

        self.tabla.setRowHeight(
            fila,
            ALTURA_FILA_TABLA,
        )

        self._recalcular_totales()

    def _fila_de_celda(
        self,
        celda: QWidget,
    ) -> int:

        for fila in range(
            self.tabla.rowCount(),
        ):

            if self.tabla.cellWidget(
                fila,
                COL_PRODUCTO,
            ) is celda:

                return fila

        return -1

    def _buscar_producto_celda(
        self,
        celda: QWidget,
    ):

        fila = self._fila_de_celda(
            celda,
        )

        if fila < 0:

            return

        self._buscar_producto(
            fila,
        )

    def _texto_producto_fila(
        self,
        fila: int,
    ) -> str:

        codigo = self._codigo_producto_fila(
            fila,
        )

        nombre = self._nombre_producto_fila(
            fila,
        )

        if (
            codigo
            and nombre
            and nombre != "Seleccione producto"
        ):

            return f"{codigo} - {nombre}"

        if nombre and nombre != "Seleccione producto":

            return nombre

        return codigo

    def _codigo_producto_fila(
        self,
        fila: int,
    ) -> str:

        celda = self.tabla.cellWidget(
            fila,
            COL_CODIGO,
        )

        if celda is None:

            return ""

        etiqueta = getattr(
            celda,
            "etiqueta",
            None,
        )

        if etiqueta is None:

            return ""

        return etiqueta.text().strip()

    def _nombre_producto_fila(
        self,
        fila: int,
    ) -> str:

        celda = self.tabla.cellWidget(
            fila,
            COL_PRODUCTO,
        )

        if celda is None:

            return ""

        etiqueta = getattr(
            celda,
            "etiqueta",
            None,
        )

        if etiqueta is None:

            return ""

        texto = etiqueta.text().strip()

        if texto == "Seleccione producto":

            return ""

        return texto

    def _buscar_producto(
        self,
        fila: int,
    ):

        dlg = ProductoLookupDialog(
            parent=self,
        )

        if not dlg.exec():

            return

        resultado = dlg.resultado

        if resultado is None:

            return

        self._aplicar_producto_en_fila(
            fila,
            resultado,
        )

    def _aplicar_producto_en_fila(
        self,
        fila: int,
        resultado,
    ):

        item = ServicioProducto.resolver_item(
            resultado.valor,
            resultado.producto_variante_id,
        )

        producto = item["producto"]

        celda_codigo = self.tabla.cellWidget(
            fila,
            COL_CODIGO,
        )

        celda = self.tabla.cellWidget(
            fila,
            COL_PRODUCTO,
        )

        if celda_codigo is not None:

            celda_codigo.producto_id = item[
                "producto_id"
            ]
            celda_codigo.producto_variante_id = item[
                "producto_variante_id"
            ]

            etiqueta_codigo = getattr(
                celda_codigo,
                "etiqueta",
                None,
            )

            if etiqueta_codigo is not None:

                etiqueta_codigo.setText(
                    item["codigo"],
                )

        if celda is not None:

            celda.producto_id = item[
                "producto_id"
            ]
            celda.producto_variante_id = item[
                "producto_variante_id"
            ]
            celda.precio_incluye_iva = bool(
                item["precio_incluye_iva"],
            )

            etiqueta = getattr(
                celda,
                "etiqueta",
                None,
            )

            if etiqueta is not None:

                etiqueta.setText(
                    item["nombre"],
                )

                etiqueta.setStyleSheet(
                    "color: #1F2937;",
                )

        spin_precio = self._widget_celda(
            fila,
            COL_PRECIO,
        )

        if spin_precio is not None:

            spin_precio.setValue(
                float(
                    item["precio_venta"]
                    or 0,
                ),
            )

        self._aplicar_precio_volumen(fila)

        celda_impuesto = self._celda_impuesto_fila(
            fila,
        )

        if (
            celda_impuesto is not None
            and item["impuesto_venta_id"]
        ):

            celda_impuesto._cargar_por_id(
                item["impuesto_venta_id"],
            )

        self._actualizar_imagen_fila(
            fila,
            producto=producto,
            codigo=item["codigo"],
            variante=item.get(
                "variante",
            ),
        )

        self._recalcular_totales()

    def _aplicar_precio_volumen(
        self,
        fila: int,
    ) -> None:
        """
        Si el producto de la fila tiene escalones de precio por
        volumen configurados, ajusta el precio unitario según la
        cantidad actual de la línea. No hace nada si el producto
        no tiene escalones definidos (no altera precios editados
        manualmente en el caso normal).
        """

        celda_producto = self.tabla.cellWidget(
            fila,
            COL_PRODUCTO,
        )

        producto_id = getattr(
            celda_producto,
            "producto_id",
            None,
        )

        if not producto_id:

            return

        spin_cantidad = self._widget_celda(
            fila,
            COL_CANTIDAD,
        )

        spin_precio = self._widget_celda(
            fila,
            COL_PRECIO,
        )

        if spin_cantidad is None or spin_precio is None:

            return

        producto = ServicioProducto.obtener_por_id(
            producto_id,
        )

        if producto is None:

            return

        precio = ServicioPrecioVolumenProducto.precio_para_cantidad(
            producto_id,
            spin_cantidad.value(),
            precio_base=float(
                producto.precio_venta or 0,
            ),
        )

        if precio is None:

            return

        spin_precio.blockSignals(True)
        spin_precio.setValue(precio)
        spin_precio.blockSignals(False)

        self._recalcular_totales()

    def _precio_incluye_iva_fila(
        self,
        fila: int,
    ) -> bool:

        celda = self.tabla.cellWidget(
            fila,
            COL_PRODUCTO,
        )

        if celda is None:

            return False

        return bool(
            getattr(
                celda,
                "precio_incluye_iva",
                False,
            )
        )

    def _recalcular_totales(self):

        lineas = self._obtener_lineas()

        resumen = ServicioCotizacion._calcular_resumen(
            lineas,
            self.celda_retefuente.valor(),
            self.celda_reteica.valor(),
            self.celda_reteiva.valor(),
        )

        for fila in range(
            self.tabla.rowCount(),
        ):

            if fila >= len(
                lineas,
            ):

                continue

            item = self.tabla.item(
                fila,
                COL_TOTAL,
            )

            if item is not None:

                item.setText(
                    f"{lineas[fila]['total_linea']:,.2f}",
                )

        self.lbl_subtotal.setText(
            f"Subtotal: $ {resumen['subtotal']:,.2f}",
        )

        self.lbl_valor_retefuente.setText(
            f"$ {resumen['retefuente']:,.2f}",
        )

        self.lbl_valor_reteica.setText(
            f"$ {resumen['reteica']:,.2f}",
        )

        self.lbl_valor_reteiva.setText(
            f"$ {resumen['reteiva']:,.2f}",
        )

        self.lbl_total.setText(
            f"Total: $ {resumen['total']:,.2f}",
        )

    def _obtener_lineas(self) -> list[dict]:

        lineas = []

        for fila in range(
            self.tabla.rowCount(),
        ):

            celda = self.tabla.cellWidget(
                fila,
                COL_PRODUCTO,
            )

            producto_id = None
            producto_variante_id = None

            if celda is not None:

                producto_id = getattr(
                    celda,
                    "producto_id",
                    None,
                )
                producto_variante_id = getattr(
                    celda,
                    "producto_variante_id",
                    None,
                )

            if (
                producto_id is None
            ):

                celda_codigo = self.tabla.cellWidget(
                    fila,
                    COL_CODIGO,
                )

                if celda_codigo is not None:

                    producto_id = getattr(
                        celda_codigo,
                        "producto_id",
                        None,
                    )
                    producto_variante_id = getattr(
                        celda_codigo,
                        "producto_variante_id",
                        None,
                    )

            descripcion = self._texto_producto_fila(
                fila,
            )

            cantidad_widget = self._widget_celda(
                fila,
                COL_CANTIDAD,
            )

            precio_widget = self._widget_celda(
                fila,
                COL_PRECIO,
            )

            celda_impuesto = self._celda_impuesto_fila(
                fila,
            )

            lineas.append(
                {
                    "producto_id": producto_id,
                    "producto_variante_id": (
                        producto_variante_id
                    ),
                    "descripcion": descripcion,
                    "cantidad": cantidad_widget.value()
                    if cantidad_widget
                    else 0,
                    "precio_unitario": precio_widget.value()
                    if precio_widget
                    else 0,
                    "impuesto_id": celda_impuesto.valor()
                    if celda_impuesto
                    else None,
                    "precio_incluye_iva": self._precio_incluye_iva_fila(
                        fila,
                    ),
                },
            )

        return lineas

    def _obtener_cabecera(self) -> dict:

        return {
            "numero": self.txt_numero.text().strip(),
            "fecha": self.fecha.date().toPython(),
            "cliente_id": self.cliente.valor(),
            "formato_impresion": self.formato.currentData(),
            "observaciones": self.observaciones.toPlainText().strip(),
            "vendedor": self.vendedor.text().strip(),
            "retefuente_id": self.celda_retefuente.valor(),
            "reteica_id": self.celda_reteica.valor(),
            "reteiva_id": self.celda_reteiva.valor(),
        }

    def guardar(self):

        try:

            cotizacion = self.datasource.guardar_completa(
                self._obtener_cabecera(),
                self._obtener_lineas(),
                self.id_registro,
            )

            self.id_registro = cotizacion.id

            self.es_edicion = True

            self.txt_numero.setText(
                cotizacion.numero,
            )

            QMessageBox.information(
                self,
                "Información",
                "Cotización guardada correctamente.",
            )

            self.guardado.emit()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                str(error),
            )

    def _datos_cotizacion_guardada(
        self,
    ):

        if self.id_registro is None:

            QMessageBox.warning(
                self,
                "Cotización",
                "Guarde la cotización antes de continuar.",
            )

            return None

        cotizacion = self.datasource.obtener_completa(
            self.id_registro,
        )

        if cotizacion is None:

            return None

        cliente = TerceroServicio.obtener_por_id(
            cotizacion.cliente_id,
        )

        nombre_cliente = ""

        if cliente is not None:

            nombre_cliente = (
                cliente.razon_social
                or cliente.nombre_completo
                or cliente.numero_documento
            )

        return (
            cotizacion,
            list(
                cotizacion.detalles,
            ),
            cliente,
            nombre_cliente,
        )

    def imprimir(self):

        datos = self._datos_cotizacion_guardada()

        if datos is None:

            return

        cotizacion, detalles, _cliente, nombre_cliente = datos

        imprimir_cotizacion(
            cotizacion,
            detalles,
            nombre_cliente,
            parent=self,
        )

    def exportar_pdf(self):

        datos = self._datos_cotizacion_guardada()

        if datos is None:

            return

        cotizacion, detalles, _cliente, nombre_cliente = datos

        exportar_pdf_cotizacion(
            cotizacion,
            detalles,
            nombre_cliente,
            parent=self,
        )

    def enviar_whatsapp(self):

        datos = self._datos_cotizacion_guardada()

        if datos is None:

            return

        cotizacion, detalles, cliente, nombre_cliente = datos

        enviar_whatsapp_cotizacion(
            cotizacion,
            detalles,
            nombre_cliente,
            cliente=cliente,
            parent=self,
        )

    def enviar_correo(self):

        datos = self._datos_cotizacion_guardada()

        if datos is None:

            return

        cotizacion, detalles, cliente, nombre_cliente = datos

        enviar_correo_cotizacion(
            cotizacion,
            detalles,
            nombre_cliente,
            cliente=cliente,
            parent=self,
        )

    def hideEvent(
        self,
        event,
    ):

        if (
            hasattr(
                self,
                "_filtro_tabla",
            )
            and hasattr(
                self,
                "tabla",
            )
            and isValid(
                self.tabla,
            )
        ):

            self.tabla.viewport().removeEventFilter(
                self._filtro_tabla,
            )

        super().hideEvent(
            event,
        )
