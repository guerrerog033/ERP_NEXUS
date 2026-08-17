from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.base.page import Page
from aplicacion.maestros.impuestos.servicios import (
    ServicioImpuesto,
)
from aplicacion.modulos.ventas.cotizaciones.formulario import (
    ALTURA_FILA_TABLA,
    ANCHO_MINIMO_TABLA,
    COL_BORRAR,
    COL_CANTIDAD,
    COL_CODIGO,
    COL_IMAGEN,
    COL_IMPUESTO,
    COL_PRECIO,
    COL_PRODUCTO,
    COL_TOTAL,
    FormularioCotizacion,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    normalizar_formato_codigo,
)
from aplicacion.modulos.ventas.facturas.datasource import (
    FacturaVentaDataSource,
)
from aplicacion.modulos.ventas.facturas.formatos_impresion import (
    formato_predeterminado_factura,
)
from aplicacion.modulos.ventas.facturas.servicios import (
    ServicioFacturaVenta,
)


ALTURA_ENCABEZADO_TABLA = 36


class FormularioFacturaVenta(
    FormularioCotizacion,
):

    titulo = "Factura de venta"

    ancho = 1160

    alto = 740

    def __init__(
        self,
        id_registro=None,
        parent=None,
    ):

        self.id_registro = id_registro

        self.es_edicion = (
            id_registro is not None
        )

        self.datasource = FacturaVentaDataSource()

        self._cargando_registro = False

        ServicioImpuesto.inicializar_predeterminados()

        Page.__init__(
            self,
            parent,
        )

    def _crear_ui(
        self,
    ):

        FormularioCotizacion._crear_ui(
            self,
        )

        self._adaptar_interfaz_factura()

    def _adaptar_interfaz_factura(
        self,
    ):

        if not self.es_edicion:

            self.txt_numero.setText(
                ServicioFacturaVenta.generar_numero(),
            )

        self._adaptar_tabla_factura()
        self._adaptar_cabecera_factura()
        self._adaptar_formas_pago()
        self._adaptar_pie_factura()
        self._adaptar_botones_factura()
        self._fijar_espacio_tabla()
        self._configurar_navegacion_tab()

        self.setMinimumWidth(
            self.ancho,
        )

        self.card.layout_principal.setContentsMargins(
            16,
            20,
            16,
            20,
        )

        self.card.contenido.setSpacing(
            0,
        )

        self._recalcular_totales()

        QTimer.singleShot(
            0,
            self._actualizar_altura_tabla,
        )

    def _adaptar_tabla_factura(
        self,
    ):

        self.tabla.setColumnHidden(
            COL_IMAGEN,
            True,
        )

        self.tabla.setHorizontalHeaderLabels(
            [
                "",
                "Código",
                "Producto",
                "Cant.",
                "Vr. Unit.",
                "Impuesto",
                "Vr. Total",
                "",
            ],
        )

        altura_fila = max(
            48,
            ALTURA_FILA_TABLA - 12,
        )

        self.tabla.verticalHeader().setDefaultSectionSize(
            altura_fila,
        )

        encabezado = self.tabla.horizontalHeader()

        encabezado.setSectionResizeMode(
            COL_CODIGO,
            QHeaderView.ResizeMode.Fixed,
        )

        encabezado.setSectionResizeMode(
            COL_PRODUCTO,
            QHeaderView.ResizeMode.Stretch,
        )

        encabezado.setSectionResizeMode(
            COL_CANTIDAD,
            QHeaderView.ResizeMode.Fixed,
        )

        encabezado.setSectionResizeMode(
            COL_PRECIO,
            QHeaderView.ResizeMode.Fixed,
        )

        encabezado.setSectionResizeMode(
            COL_IMPUESTO,
            QHeaderView.ResizeMode.Fixed,
        )

        encabezado.setSectionResizeMode(
            COL_TOTAL,
            QHeaderView.ResizeMode.Fixed,
        )

        encabezado.setSectionResizeMode(
            COL_BORRAR,
            QHeaderView.ResizeMode.Fixed,
        )

        self.tabla.setColumnWidth(
            COL_CODIGO,
            120,
        )

        self.tabla.setColumnWidth(
            COL_CANTIDAD,
            88,
        )

        self.tabla.setColumnWidth(
            COL_PRECIO,
            110,
        )

        self.tabla.setColumnWidth(
            COL_IMPUESTO,
            130,
        )

        self.tabla.setColumnWidth(
            COL_TOTAL,
            110,
        )

        self.tabla.setColumnWidth(
            COL_BORRAR,
            44,
        )

        self.tabla.setMinimumWidth(
            ANCHO_MINIMO_TABLA,
        )

        encabezado.setVisible(
            True,
        )

        encabezado.setFixedHeight(
            ALTURA_ENCABEZADO_TABLA,
        )

        encabezado.setHighlightSections(
            True,
        )

        self._aplicar_estilo_tabla_factura()

        self._reemplazar_scroll_tabla()

        for fila in range(
            self.tabla.rowCount(),
        ):

            self.tabla.setRowHeight(
                fila,
                altura_fila,
            )

        self._actualizar_altura_tabla()

    def _widget_contenedor_tabla(
        self,
    ) -> QWidget:

        panel = getattr(
            self,
            "panel_tabla",
            None,
        )

        if panel is not None:

            return panel

        return self.scroll_tabla

    def _aplicar_estilo_tabla_factura(
        self,
    ) -> None:

        estilo = self.tabla.styleSheet()

        if "QTableWidget::viewport" not in estilo:

            estilo = estilo.replace(
                "QTableWidget {",
                "QTableWidget::viewport {",
                1,
            )

        if "QHeaderView::section" not in estilo:

            estilo = (
                estilo
                + """
            QHeaderView::section {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3A7BC5,
                    stop:1 #1B4F8A
                );
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
            """
            )

        self.tabla.setStyleSheet(
            estilo,
        )

    def _reemplazar_scroll_tabla(
        self,
    ) -> None:

        indice = self.card.contenido.indexOf(
            self.scroll_tabla,
        )

        if indice < 0:

            return

        layout_anterior = (
            self.contenedor_tabla.layout()
        )

        if layout_anterior is not None:

            layout_anterior.removeWidget(
                self.tabla,
            )

        self.tabla.setParent(
            None,
        )

        self.card.contenido.removeWidget(
            self.scroll_tabla,
        )

        self.scroll_tabla.hide()

        self.panel_tabla = QWidget()

        self.panel_tabla.setObjectName(
            "PanelTablaFactura",
        )

        layout_panel = QVBoxLayout(
            self.panel_tabla,
        )

        layout_panel.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout_panel.setSpacing(
            0,
        )

        encabezado_tabla = self.tabla.horizontalHeader()

        encabezado_tabla.setVisible(
            True,
        )

        encabezado_tabla.setFixedHeight(
            ALTURA_ENCABEZADO_TABLA,
        )

        layout_panel.addWidget(
            self.tabla,
        )

        self.panel_tabla.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.card.contenido.insertWidget(
            indice,
            self.panel_tabla,
        )

    def _actualizar_altura_tabla(
        self,
    ) -> None:

        if not hasattr(
            self,
            "panel_tabla",
        ):

            return

        encabezado = self.tabla.horizontalHeader()

        encabezado.setVisible(
            True,
        )

        encabezado.setFixedHeight(
            ALTURA_ENCABEZADO_TABLA,
        )

        filas = max(
            self.tabla.rowCount(),
            1,
        )

        altura_fila = (
            self.tabla.rowHeight(
                0,
            )
            if self.tabla.rowCount() > 0
            else self.tabla.verticalHeader().defaultSectionSize()
        )

        marco = self.tabla.frameWidth() * 2

        altura_cuerpo = (
            filas * altura_fila
            + marco
            + 2
        )

        max_filas = 8

        altura_maxima_cuerpo = (
            max_filas * altura_fila
            + marco
            + 2
        )

        altura_encabezado = encabezado.height()

        altura_tabla = (
            altura_encabezado
            + altura_cuerpo
        )

        altura_maxima_tabla = (
            altura_encabezado
            + altura_maxima_cuerpo
        )

        self.tabla.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        if altura_tabla > altura_maxima_tabla:

            self.tabla.setFixedHeight(
                altura_maxima_tabla,
            )

            self.tabla.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded,
            )

        else:

            self.tabla.setFixedHeight(
                altura_tabla,
            )

            self.tabla.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
            )

        self.panel_tabla.setFixedHeight(
            self.tabla.height(),
        )

        self.tabla.updateGeometry()

    def showEvent(
        self,
        event,
    ):

        super().showEvent(
            event,
        )

        QTimer.singleShot(
            0,
            self._actualizar_altura_tabla,
        )

    def _adaptar_cabecera_factura(
        self,
    ):

        cabecera_item = self.card.contenido.itemAt(
            0,
        )

        cabecera_vieja = (
            cabecera_item.widget()
            if cabecera_item is not None
            else None
        )

        if cabecera_vieja is None:

            return

        self.formato.hide()

        self.formato.setParent(
            self,
        )

        campos = (
            self.txt_numero,
            self.fecha,
            self.cliente,
            self.vendedor,
        )

        for campo in campos:

            campo.setParent(
                None,
            )

        self.card.contenido.removeWidget(
            cabecera_vieja,
        )

        cabecera_vieja.deleteLater()

        cabecera = QWidget()

        grid = QGridLayout(
            cabecera,
        )

        grid.setContentsMargins(
            16,
            10,
            16,
            0,
        )

        grid.setHorizontalSpacing(
            12,
        )

        grid.setVerticalSpacing(
            10,
        )

        etiqueta_numero = QLabel(
            "Número",
        )

        etiqueta_fecha = QLabel(
            "Fecha de elaboración",
        )

        etiqueta_cliente = QLabel(
            "Cliente",
        )

        etiqueta_vendedor = QLabel(
            "Vendedor",
        )

        etiqueta_tipo = QLabel(
            "Tipo",
        )

        etiqueta_contacto = QLabel(
            "Contacto",
        )

        for etiqueta in (
            etiqueta_numero,
            etiqueta_fecha,
            etiqueta_cliente,
            etiqueta_vendedor,
            etiqueta_tipo,
            etiqueta_contacto,
        ):

            etiqueta.setAlignment(
                Qt.AlignmentFlag.AlignLeft
                | Qt.AlignmentFlag.AlignVCenter,
            )

        self.cmb_tipo = QComboBox()

        self.cmb_tipo.addItems(
            [
                "Factura de venta",
                "Factura de exportación",
            ],
        )

        self.cmb_contacto = QComboBox()

        self.cmb_contacto.setEditable(
            True,
        )

        self.cmb_contacto.addItem(
            "",
        )

        etiqueta_moneda = QLabel(
            "Moneda de referencia",
        )

        etiqueta_tasa_cambio = QLabel(
            "Tasa de cambio",
        )

        self.cmb_moneda_referencia = QComboBox()

        self.cmb_moneda_referencia.addItem(
            "COP (sin referencia)",
            "",
        )

        self.cmb_moneda_referencia.addItem(
            "USD",
            "USD",
        )

        self.cmb_moneda_referencia.addItem(
            "EUR",
            "EUR",
        )

        self.spin_tasa_cambio_referencia = (
            QDoubleSpinBox()
        )

        self.spin_tasa_cambio_referencia.setRange(
            0,
            9999999,
        )

        self.spin_tasa_cambio_referencia.setDecimals(
            2,
        )

        self.spin_tasa_cambio_referencia.setToolTip(
            "Valor en COP de 1 unidad de la moneda de "
            "referencia (ej. TRM del día). Los totales de "
            "la factura siempre quedan en COP.",
        )

        altura_campo = 34

        for campo in (
            self.fecha,
            self.vendedor,
            self.cmb_tipo,
            self.cmb_contacto,
            self.cliente,
        ):

            campo.setFixedHeight(
                altura_campo,
            )

        self.fecha.setMinimumWidth(
            150,
        )

        self.fecha.setMaximumWidth(
            self.fecha.sizeHint().width() * 100,
        )

        for campo in (
            self.fecha,
            self.vendedor,
            self.cmb_tipo,
            self.cmb_contacto,
        ):

            campo.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
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
            etiqueta_vendedor,
            2,
            0,
        )

        grid.addWidget(
            self.vendedor,
            2,
            1,
        )

        grid.addWidget(
            etiqueta_tipo,
            2,
            2,
        )

        grid.addWidget(
            self.cmb_tipo,
            2,
            3,
        )

        grid.addWidget(
            etiqueta_contacto,
            3,
            0,
        )

        grid.addWidget(
            self.cmb_contacto,
            3,
            1,
            1,
            3,
        )

        grid.addWidget(
            etiqueta_moneda,
            4,
            0,
        )

        grid.addWidget(
            self.cmb_moneda_referencia,
            4,
            1,
        )

        grid.addWidget(
            etiqueta_tasa_cambio,
            4,
            2,
        )

        grid.addWidget(
            self.spin_tasa_cambio_referencia,
            4,
            3,
        )

        grid.setColumnMinimumWidth(
            0,
            140,
        )

        grid.setColumnMinimumWidth(
            2,
            140,
        )

        grid.setColumnStretch(
            1,
            1,
        )

        grid.setColumnStretch(
            3,
            1,
        )

        cabecera.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.card.contenido.insertWidget(
            0,
            cabecera,
        )

        pendiente = getattr(
            self,
            "_moneda_referencia_pendiente",
            None,
        )

        if pendiente is not None:

            moneda, tasa = pendiente

            indice_moneda = (
                self.cmb_moneda_referencia.findData(
                    moneda or "",
                )
            )

            self.cmb_moneda_referencia.setCurrentIndex(
                indice_moneda if indice_moneda >= 0 else 0,
            )

            self.spin_tasa_cambio_referencia.setValue(
                float(tasa or 0),
            )

    def _adaptar_formas_pago(
        self,
    ):

        panel_pagos = QWidget()

        panel_pagos.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout_pagos = QVBoxLayout(
            panel_pagos,
        )

        layout_pagos.setContentsMargins(
            16,
            0,
            16,
            0,
        )

        layout_pagos.setSpacing(
            6,
        )

        etiqueta_pagos = QLabel(
            "Formas de pago",
        )

        etiqueta_pagos.setStyleSheet(
            "font-weight:600;color:#1B4F8A;",
        )

        fila_pago = QHBoxLayout()

        fila_pago.setSpacing(
            12,
        )

        self.cmb_forma_pago = QComboBox()

        self.cmb_forma_pago.addItems(
            [
                "Selecciona forma de pago",
                "Efectivo",
                "Transferencia",
                "Tarjeta",
                "Crédito",
            ],
        )

        self.cmb_forma_pago.setMinimumWidth(
            280,
        )

        self.cmb_forma_pago.setMaximumWidth(
            360,
        )

        fila_pago.addWidget(
            self.cmb_forma_pago,
        )

        fila_pago.addStretch()

        layout_pagos.addWidget(
            etiqueta_pagos,
        )

        layout_pagos.addLayout(
            fila_pago,
        )

        self.panel_pagos = panel_pagos

    def _fijar_espacio_tabla(
        self,
    ) -> None:

        return

    def _adaptar_pie_factura(
        self,
    ):

        panel_observaciones = (
            self.observaciones.parentWidget()
        )

        panel_totales = self.lbl_total.parentWidget()

        if panel_observaciones is not None:

            panel_observaciones.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred,
            )

            panel_observaciones.setMinimumWidth(
                280,
            )

        self.observaciones.setMinimumHeight(
            96,
        )

        self.observaciones.setMaximumHeight(
            120,
        )

        if panel_totales is not None:

            layout_totales = panel_totales.layout()

            if layout_totales is not None:

                layout_totales.setContentsMargins(
                    0,
                    4,
                    0,
                    4,
                )

                layout_totales.setSpacing(
                    4,
                )

            panel_totales.setMinimumWidth(
                260,
            )

            panel_totales.setMaximumWidth(
                300,
            )

        indice_acciones = None

        for indice in range(
            self.card.contenido.count(),
        ):

            item = self.card.contenido.itemAt(
                indice,
            )

            if item is None:

                continue

            layout = item.layout()

            if (
                layout is not None
                and layout.indexOf(
                    self.btn_agregar_linea,
                ) >= 0
            ):

                indice_acciones = indice

                break

        if (
            indice_acciones is None
            or panel_observaciones is None
            or panel_totales is None
        ):

            return

        panel_pagos = getattr(
            self,
            "panel_pagos",
            None,
        )

        self.btn_agregar_linea.setParent(
            None,
        )

        if panel_pagos is not None:

            panel_pagos.setParent(
                None,
            )

        panel_observaciones.setParent(
            None,
        )

        panel_totales.setParent(
            None,
        )

        self.card.contenido.takeAt(
            indice_acciones,
        )

        pie = QWidget()

        layout_pie = QVBoxLayout(
            pie,
        )

        layout_pie.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout_pie.setSpacing(
            8,
        )

        fila_superior = QHBoxLayout()

        fila_superior.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        fila_superior.addWidget(
            self.btn_agregar_linea,
        )

        fila_superior.addWidget(
            panel_observaciones,
            1,
        )

        fila_superior.addWidget(
            panel_totales,
        )

        if panel_pagos is not None:

            layout_pie.addWidget(
                panel_pagos,
            )

        layout_pie.addLayout(
            fila_superior,
        )

        pie.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.card.contenido.insertWidget(
            indice_acciones,
            pie,
        )

    def _adaptar_botones_factura(
        self,
    ):

        self.btn_imprimir.hide()
        self.btn_whatsapp.hide()
        self.btn_correo.hide()

        self.btn_pdf.setText(
            "Enviar",
        )

        try:

            self.btn_pdf.clicked.disconnect()

        except TypeError:

            pass

        self.btn_pdf.clicked.connect(
            self._enviar_factura,
        )

        self.btn_guardar.setText(
            "Guardar",
        )

    def _boton_producto_fila(
        self,
        fila: int,
    ) -> QPushButton | None:

        celda = self.tabla.cellWidget(
            fila,
            COL_PRODUCTO,
        )

        if celda is None:

            return None

        layout = celda.layout()

        if (
            layout is None
            or layout.count() < 2
        ):

            return None

        boton = layout.itemAt(
            1,
        ).widget()

        if isinstance(
            boton,
            QPushButton,
        ):

            return boton

        return None

    def _fila_tiene_producto(
        self,
        fila: int,
    ) -> bool:

        celda = self.tabla.cellWidget(
            fila,
            COL_PRODUCTO,
        )

        if celda is None:

            return False

        return (
            getattr(
                celda,
                "producto_id",
                None,
            )
            is not None
        )

    def _widgets_tab_fila(
        self,
        fila: int,
    ) -> list[QWidget]:

        widgets: list[QWidget] = []

        boton = self._boton_producto_fila(
            fila,
        )

        if boton is not None:

            widgets.append(
                boton,
            )

        for columna in (
            COL_CANTIDAD,
            COL_PRECIO,
        ):

            widget = self._widget_celda(
                fila,
                columna,
            )

            if widget is not None:

                widgets.append(
                    widget,
                )

        celda_impuesto = self._celda_impuesto_fila(
            fila,
        )

        if (
            celda_impuesto is not None
            and hasattr(
                celda_impuesto,
                "combo",
            )
        ):

            widgets.append(
                celda_impuesto.combo,
            )

        return widgets

    def _configurar_navegacion_tab(
        self,
    ) -> None:

        if not hasattr(
            self,
            "cmb_tipo",
        ):

            return

        cabecera: list[QWidget] = [
            self.fecha,
            self.cliente.btn,
            self.vendedor,
            self.cmb_tipo,
            self.cmb_contacto,
        ]

        for widget in cabecera:

            widget.setFocusPolicy(
                Qt.FocusPolicy.StrongFocus,
            )

        self.cliente.txt.setFocusPolicy(
            Qt.FocusPolicy.NoFocus,
        )

        anterior: QWidget | None = None

        for widget in cabecera:

            if anterior is not None:

                QWidget.setTabOrder(
                    anterior,
                    widget,
                )

            anterior = widget

        for fila in range(
            self.tabla.rowCount(),
        ):

            for widget in self._widgets_tab_fila(
                fila,
            ):

                widget.setFocusPolicy(
                    Qt.FocusPolicy.StrongFocus,
                )

                if anterior is not None:

                    QWidget.setTabOrder(
                        anterior,
                        widget,
                    )

                anterior = widget

        if hasattr(
            self,
            "cmb_forma_pago",
        ):

            self.cmb_forma_pago.setFocusPolicy(
                Qt.FocusPolicy.StrongFocus,
            )

            if anterior is not None:

                QWidget.setTabOrder(
                    anterior,
                    self.cmb_forma_pago,
                )

            anterior = self.cmb_forma_pago

        self.observaciones.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus,
        )

        if anterior is not None:

            QWidget.setTabOrder(
                anterior,
                self.observaciones,
            )

        anterior = self.observaciones

        for boton in (
            self.btn_pdf,
            self.btn_guardar,
            self.btn_cancelar,
        ):

            boton.setFocusPolicy(
                Qt.FocusPolicy.StrongFocus,
            )

            if anterior is not None:

                QWidget.setTabOrder(
                    anterior,
                    boton,
                )

            anterior = boton

    def _asegurar_fila_vacia_final(
        self,
        *,
        enfocar_nueva: bool = True,
    ) -> None:

        if self._cargando_registro:

            return

        if self.tabla.rowCount() == 0:

            self._agregar_linea()

            return

        ultima = (
            self.tabla.rowCount()
            - 1
        )

        if not self._fila_tiene_producto(
            ultima,
        ):

            return

        self._agregar_linea()

        if not enfocar_nueva:

            return

        nueva = (
            self.tabla.rowCount()
            - 1
        )

        boton = self._boton_producto_fila(
            nueva,
        )

        if boton is not None:

            boton.setFocus()

    def _aplicar_producto_en_fila(
        self,
        fila: int,
        resultado,
    ) -> None:

        super()._aplicar_producto_en_fila(
            fila,
            resultado,
        )

        spin_cantidad = self._widget_celda(
            fila,
            COL_CANTIDAD,
        )

        if spin_cantidad is not None:

            spin_cantidad.setFocus()

            editor = spin_cantidad.lineEdit()

            if editor is not None:

                editor.selectAll()

        self._asegurar_fila_vacia_final(
            enfocar_nueva=False,
        )

        self._configurar_navegacion_tab()

        self._actualizar_altura_tabla()

    def _quitar_fila_celda(
        self,
        celda: QWidget,
    ) -> None:

        super()._quitar_fila_celda(
            celda,
        )

        self._asegurar_fila_vacia_final()

        self._configurar_navegacion_tab()

        self._actualizar_altura_tabla()

    def _agregar_linea(
        self,
        *args,
        **kwargs,
    ):

        super()._agregar_linea(
            *args,
            **kwargs,
        )

        altura_fila = max(
            48,
            ALTURA_FILA_TABLA - 12,
        )

        fila = self.tabla.rowCount() - 1

        if fila >= 0:

            self.tabla.setRowHeight(
                fila,
                altura_fila,
            )

        self._configurar_navegacion_tab()

        self._actualizar_altura_tabla()

    def _cargar_registro(
        self,
    ):

        factura = self.datasource.obtener_completa(
            self.id_registro,
        )

        if factura is None:

            return

        self._cargando_registro = True

        self.txt_numero.setText(
            factura.numero,
        )

        self.fecha.setDate(
            factura.fecha,
        )

        self.cliente.setValue(
            factura.cliente_id,
        )

        indice = self.formato.findData(
            normalizar_formato_codigo(
                getattr(
                    factura,
                    "formato_impresion",
                    None,
                )
                or formato_predeterminado_factura(),
            ),
        )

        if indice >= 0:

            self.formato.setCurrentIndex(
                indice,
            )

        observaciones = str(
            factura.observaciones or "",
        ).strip()

        vendedor = ""

        if observaciones.startswith(
            "Vendedor:",
        ):

            partes = observaciones.split(
                "\n",
                1,
            )

            vendedor = partes[0].replace(
                "Vendedor:",
                "",
            ).strip()

            observaciones = (
                partes[1].strip()
                if len(partes) > 1
                else ""
            )

        self.observaciones.setPlainText(
            observaciones,
        )

        self.vendedor.setText(
            vendedor,
        )

        self._moneda_referencia_pendiente = (
            factura.moneda_referencia,
            factura.tasa_cambio_referencia,
        )

        self.tabla.setRowCount(
            0,
        )

        for detalle in factura.detalles:

            producto = None

            if detalle.producto_id:

                from aplicacion.maestros.productos.servicios import (
                    ServicioProducto,
                )

                producto = ServicioProducto.obtener_por_id(
                    detalle.producto_id,
                )

            codigo = ""
            nombre = detalle.descripcion or ""

            if producto is not None:

                codigo = producto.codigo or ""
                nombre = producto.nombre or nombre

            elif " - " in nombre:

                partes = nombre.split(
                    " - ",
                    1,
                )

                codigo = partes[0]
                nombre = partes[1]

            self._agregar_linea(
                producto_id=detalle.producto_id,
                producto_variante_id=getattr(
                    detalle,
                    "producto_variante_id",
                    None,
                ),
                codigo=codigo,
                nombre=nombre,
                cantidad=detalle.cantidad,
                precio=detalle.precio_unitario,
                impuesto_id=detalle.impuesto_id,
                precio_incluye_iva=bool(
                    getattr(
                        detalle,
                        "precio_incluye_iva",
                        False,
                    ),
                ),
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

        self._recalcular_totales()

        self._cargando_registro = False

        self._asegurar_fila_vacia_final()

        self._configurar_navegacion_tab()

        self._actualizar_altura_tabla()

    def _obtener_cabecera(
        self,
    ) -> dict:

        return {
            "numero": self.txt_numero.text().strip(),
            "fecha": self.fecha.date().toPython(),
            "cliente_id": self.cliente.valor(),
            "formato_impresion": normalizar_formato_codigo(
                self.formato.currentData()
                or formato_predeterminado_factura(),
            ),
            "observaciones": self.observaciones.toPlainText().strip(),
            "vendedor": self.vendedor.text().strip(),
            "retefuente_id": self.celda_retefuente.valor(),
            "reteica_id": self.celda_reteica.valor(),
            "reteiva_id": self.celda_reteiva.valor(),
            "moneda_referencia": (
                self.cmb_moneda_referencia.currentData()
            ),
            "tasa_cambio_referencia": (
                self.spin_tasa_cambio_referencia.value()
            ),
        }

    def guardar(
        self,
    ):

        try:

            factura = self.datasource.guardar_completa(
                self._obtener_cabecera(),
                self._obtener_lineas(),
                self.id_registro,
            )

            self.id_registro = factura.id

            self.es_edicion = True

            self.txt_numero.setText(
                factura.numero,
            )

            QMessageBox.information(
                self,
                "Información",
                "Factura guardada correctamente.",
            )

            self.guardado.emit()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                str(error),
            )

    def _enviar_factura(
        self,
    ):

        if self.id_registro is None:

            QMessageBox.warning(
                self,
                "Factura",
                "Guarde la factura antes de enviar.",
            )

            return

        try:

            self.datasource.emitir_electronica(
                self.id_registro,
            )

            QMessageBox.information(
                self,
                "Factura",
                "Proceso de envío iniciado.",
            )

        except Exception as error:

            QMessageBox.warning(
                self,
                "Factura",
                str(error),
            )
