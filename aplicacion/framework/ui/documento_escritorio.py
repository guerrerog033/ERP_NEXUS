"""
Piezas para las pantallas de documentos (facturas, cotizaciones,
compras) con estilo de programa contable de escritorio:

- Barra de título del documento con el número a la derecha
  (World Office: "Factura de Venta ........ FV-1681").
- Barra de acciones con íconos arriba (Siigo / World Office).
- Cajas con marco titulado: "Información del cliente" y "Datos del
  documento", con NIT, dirección, teléfono y saldo de cartera del
  tercero (Magister).
- Fila de totales bajo el detalle (Magister).
- Pestañas abajo: Observaciones / Formas de pago / Impuestos
  (Magister) y caja de totales con encabezado (World Office).
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


def formato_moneda(
    valor,
) -> str:

    try:

        numero = float(
            valor or 0,
        )

    except (
        TypeError,
        ValueError,
    ):

        numero = 0.0

    texto = f"{numero:,.2f}"

    # 1,234,567.89 -> 1.234.567,89
    texto = texto.replace(
        ",",
        "_",
    ).replace(
        ".",
        ",",
    ).replace(
        "_",
        ".",
    )

    return f"$ {texto}"


# =========================================================
# Barra de título
# =========================================================


class BarraTituloDocumento(QFrame):

    def __init__(
        self,
        titulo: str,
        color: str = "#1E3A5F",
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "DocumentoBarraTitulo",
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        layout = QHBoxLayout(
            self,
        )

        layout.setContentsMargins(
            14,
            6,
            8,
            6,
        )

        layout.setSpacing(
            10,
        )

        self.lbl_titulo = QLabel(
            titulo,
        )

        self.lbl_titulo.setObjectName(
            "DocumentoBarraTituloTexto",
        )

        self.lbl_estado = QLabel(
            "",
        )

        self.lbl_estado.setObjectName(
            "DocumentoEstado",
        )

        self.lbl_estado.hide()

        self.caja_numero = QFrame()

        self.caja_numero.setObjectName(
            "DocumentoCajaNumero",
        )

        self._layout_numero = QHBoxLayout(
            self.caja_numero,
        )

        self._layout_numero.setContentsMargins(
            10,
            2,
            10,
            2,
        )

        self._layout_numero.setSpacing(
            6,
        )

        etiqueta = QLabel(
            "No.",
        )

        etiqueta.setObjectName(
            "DocumentoCajaNumeroEtiqueta",
        )

        self._layout_numero.addWidget(
            etiqueta,
        )

        layout.addWidget(
            self.lbl_titulo,
        )

        layout.addWidget(
            self.lbl_estado,
        )

        layout.addStretch(
            1,
        )

        layout.addWidget(
            self.caja_numero,
        )

        self.set_color(
            color,
        )

    def set_color(
        self,
        color: str,
    ) -> None:

        self.setStyleSheet(
            "QFrame#DocumentoBarraTitulo {"
            f" border-left: 6px solid {color};"
            "}",
        )

    def set_numero_widget(
        self,
        widget: QWidget,
    ) -> None:

        widget.setObjectName(
            "DocumentoNumero",
        )

        self._layout_numero.addWidget(
            widget,
        )

    def set_estado(
        self,
        texto: str,
    ) -> None:

        self.lbl_estado.setText(
            texto or "",
        )

        self.lbl_estado.setVisible(
            bool(texto),
        )


# =========================================================
# Barra de acciones
# =========================================================

ICONOS_ACCION = {
    "guardar": "guardar",
    "enviar": "correo",
    "imprimir": "imprimir",
    "pdf": "pdf",
    "correo": "correo",
    "whatsapp": "nuevo",
    "cancelar": "cerrar",
    "importar": "nuevo",
    "copiar": "copiar",
    "anular": "anular",
    "contabilizar": "contabilizar",
}


class BarraAccionesDocumento(QFrame):
    """Fila de botones con ícono arriba del documento."""

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "DocumentoBarraAcciones",
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        self._layout = QHBoxLayout(
            self,
        )

        self._layout.setContentsMargins(
            6,
            3,
            6,
            3,
        )

        self._layout.setSpacing(
            3,
        )

        self._fin = QHBoxLayout()

        self._fin.setSpacing(
            3,
        )

        self._layout.addStretch(
            1,
        )

        self._layout.addLayout(
            self._fin,
        )

    def _preparar(
        self,
        boton: QPushButton,
        icono: str | None,
        atajo: str | None,
    ) -> None:

        from aplicacion.framework.ui.iconos import icono_accion

        if boton.objectName() != "BotonPrimario":

            boton.setObjectName(
                "BotonAccionDocumento",
            )

        if icono:

            color = (
                "#FFFFFF"
                if boton.objectName() == "BotonPrimario"
                else "#1E3A5F"
            )

            boton.setIcon(
                icono_accion(
                    icono,
                    color,
                    16,
                ),
            )

            boton.setIconSize(
                QSize(
                    16,
                    16,
                ),
            )

        if atajo:

            texto_ayuda = boton.toolTip() or boton.text()

            if atajo not in texto_ayuda:

                boton.setToolTip(
                    f"{boton.text()} ({atajo})",
                )

        boton.setMinimumHeight(
            26,
        )

        boton.setMinimumWidth(
            0,
        )

        boton.setFocusPolicy(
            Qt.FocusPolicy.TabFocus,
        )

    def agregar(
        self,
        boton: QPushButton,
        icono: str | None = None,
        atajo: str | None = None,
    ) -> None:

        self._preparar(
            boton,
            icono,
            atajo,
        )

        indice = self._layout.count() - 2

        self._layout.insertWidget(
            max(
                0,
                indice,
            ),
            boton,
        )

    def agregar_separador(
        self,
    ) -> None:

        linea = QFrame()

        linea.setObjectName(
            "ToolbarSeparador",
        )

        linea.setFrameShape(
            QFrame.Shape.VLine,
        )

        linea.setFixedWidth(
            1,
        )

        linea.setFixedHeight(
            20,
        )

        indice = self._layout.count() - 2

        self._layout.insertWidget(
            max(
                0,
                indice,
            ),
            linea,
        )

    def agregar_al_final(
        self,
        boton: QPushButton,
        icono: str | None = None,
        atajo: str | None = None,
    ) -> None:

        self._preparar(
            boton,
            icono,
            atajo,
        )

        self._fin.addWidget(
            boton,
        )


# =========================================================
# Cajas con marco titulado
# =========================================================


class CajaDatos(QGroupBox):

    def __init__(
        self,
        titulo: str,
        parent=None,
    ):

        super().__init__(
            titulo,
            parent,
        )

        self.setObjectName(
            "CajaDocumento",
        )

        self.grid = QGridLayout(
            self,
        )

        self.grid.setContentsMargins(
            10,
            6,
            10,
            8,
        )

        self.grid.setHorizontalSpacing(
            10,
        )

        self.grid.setVerticalSpacing(
            5,
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

    @staticmethod
    def etiqueta(
        texto: str,
    ) -> QLabel:

        lbl = QLabel(
            texto,
        )

        lbl.setObjectName(
            "CajaDocumentoEtiqueta",
        )

        return lbl

    @staticmethod
    def dato(
        texto: str = "",
    ) -> QLabel:

        lbl = QLabel(
            texto,
        )

        lbl.setObjectName(
            "CajaDocumentoDato",
        )

        lbl.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse,
        )

        lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        lbl.setMinimumWidth(
            60,
        )

        return lbl


class PanelTercero(CajaDatos):
    """
    "Información del cliente / proveedor": el buscador del tercero
    y, al elegirlo, su NIT, dirección, teléfono y saldo de cartera.
    """

    def __init__(
        self,
        titulo: str,
        lookup: QWidget,
        *,
        etiqueta: str = "Cliente",
        cartera: str = "cxc",
        parent=None,
    ):

        super().__init__(
            titulo,
            parent,
        )

        self._cartera = cartera

        self.lookup = lookup

        self.lbl_nit = self.dato()
        self.lbl_direccion = self.dato()
        self.lbl_telefono = self.dato()
        self.lbl_saldo = self.dato()

        self.lbl_saldo.setObjectName(
            "CajaDocumentoSaldo",
        )

        self.grid.addWidget(
            self.etiqueta(
                etiqueta,
            ),
            0,
            0,
        )

        self.grid.addWidget(
            lookup,
            0,
            1,
            1,
            3,
        )

        self.grid.addWidget(
            self.etiqueta(
                "NIT / CC",
            ),
            1,
            0,
        )

        self.grid.addWidget(
            self.lbl_nit,
            1,
            1,
        )

        self.grid.addWidget(
            self.etiqueta(
                "Teléfono",
            ),
            1,
            2,
        )

        self.grid.addWidget(
            self.lbl_telefono,
            1,
            3,
        )

        self.grid.addWidget(
            self.etiqueta(
                "Dirección",
            ),
            2,
            0,
        )

        self.grid.addWidget(
            self.lbl_direccion,
            2,
            1,
        )

        self.grid.addWidget(
            self.etiqueta(
                "Saldo cartera",
            ),
            2,
            2,
        )

        self.grid.addWidget(
            self.lbl_saldo,
            2,
            3,
        )

        self.grid.setColumnStretch(
            1,
            2,
        )

        self.grid.setColumnStretch(
            3,
            1,
        )

        self.grid.setColumnMinimumWidth(
            0,
            86,
        )

        self.limpiar()

        senal = getattr(
            lookup,
            "seleccionado",
            None,
        )

        if senal is not None:

            senal.connect(
                self._al_seleccionar,
            )

    def usar_campo_nit(
        self,
        widget: QWidget,
    ) -> None:
        """Pone un campo propio (p. ej. el NIT del XML) en lugar del dato."""

        self.grid.removeWidget(
            self.lbl_nit,
        )

        self.lbl_nit.hide()

        self.grid.addWidget(
            widget,
            1,
            1,
        )

        self._campo_nit = widget

    def agregar_fila(
        self,
        etiqueta: str,
        widget: QWidget,
    ) -> None:

        fila = self.grid.rowCount()

        self.grid.addWidget(
            self.etiqueta(
                etiqueta,
            ),
            fila,
            0,
        )

        self.grid.addWidget(
            widget,
            fila,
            1,
            1,
            3,
        )

    def limpiar(
        self,
    ) -> None:

        for etiqueta in (
            self.lbl_nit,
            self.lbl_direccion,
            self.lbl_telefono,
            self.lbl_saldo,
        ):

            etiqueta.setText(
                "—",
            )

        self.lbl_saldo.setProperty(
            "vencido",
            False,
        )

    def _al_seleccionar(
        self,
        resultado,
    ) -> None:

        valor = getattr(
            resultado,
            "valor",
            resultado,
        )

        if not valor:

            self.limpiar()

            return

        try:

            self.mostrar_tercero(
                int(
                    valor,
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            self.limpiar()

    def mostrar_tercero(
        self,
        tercero_id: int | None,
    ) -> None:

        if not tercero_id:

            self.limpiar()

            return

        try:

            from aplicacion.maestros.terceros.servicio import (
                TerceroServicio,
            )

            tercero = TerceroServicio.obtener_por_id(
                tercero_id,
            )

        except Exception:

            tercero = None

        if tercero is None:

            self.limpiar()

            return

        documento = str(
            getattr(
                tercero,
                "numero_documento",
                "",
            )
            or "",
        )

        dv = str(
            getattr(
                tercero,
                "dv",
                "",
            )
            or "",
        )

        self.lbl_nit.setText(
            f"{documento}-{dv}" if dv else (documento or "—"),
        )

        direccion = ", ".join(
            parte
            for parte in (
                getattr(
                    tercero,
                    "direccion",
                    "",
                )
                or "",
                getattr(
                    tercero,
                    "ciudad",
                    "",
                )
                or "",
            )
            if parte
        )

        self.lbl_direccion.setText(
            direccion or "—",
        )

        telefono = (
            getattr(
                tercero,
                "telefono",
                "",
            )
            or getattr(
                tercero,
                "celular",
                "",
            )
            or ""
        )

        self.lbl_telefono.setText(
            telefono or "—",
        )

        self._mostrar_saldo(
            tercero_id,
        )

    def _mostrar_saldo(
        self,
        tercero_id: int,
    ) -> None:

        saldo = None
        vencido = 0.0

        try:

            from aplicacion.modulos.cartera.servicios import (
                ServicioCartera,
            )

            if self._cartera == "cxc":

                resumen = ServicioCartera.resumen_cliente_cxc(
                    tercero_id,
                )

                saldo = resumen.get(
                    "saldo_total",
                    0,
                )

                vencido = float(
                    resumen.get(
                        "saldo_vencido",
                        0,
                    )
                    or 0,
                )

            elif self._cartera == "cxp":

                filas = ServicioCartera.listar_cxp(
                    tercero_id=tercero_id,
                )

                saldo = sum(
                    float(
                        fila.get(
                            "saldo",
                            0,
                        )
                        or 0,
                    )
                    for fila in filas
                )

        except Exception:

            saldo = None

        if saldo is None:

            self.lbl_saldo.setText(
                "—",
            )

            return

        texto = formato_moneda(
            saldo,
        )

        if vencido > 0:

            texto += f"  (vencido {formato_moneda(vencido)})"

        self.lbl_saldo.setText(
            texto,
        )

        self.lbl_saldo.setProperty(
            "vencido",
            vencido > 0,
        )

        self.lbl_saldo.style().unpolish(
            self.lbl_saldo,
        )

        self.lbl_saldo.style().polish(
            self.lbl_saldo,
        )


# =========================================================
# Resumen de impuestos (pestaña "Impuestos")
# =========================================================


class TablaResumenImpuestos(QTableWidget):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            0,
            4,
            parent,
        )

        self.setObjectName(
            "TablaResumenImpuestos",
        )

        self.setHorizontalHeaderLabels(
            [
                "Impuesto",
                "Base",
                "Tarifa",
                "Valor",
            ],
        )

        self.verticalHeader().setVisible(
            False,
        )

        self.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers,
        )

        self.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection,
        )

        self.setFocusPolicy(
            Qt.FocusPolicy.NoFocus,
        )

        self.setAlternatingRowColors(
            True,
        )

        cabecera = self.horizontalHeader()

        cabecera.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )

        for columna in (
            1,
            2,
            3,
        ):

            cabecera.setSectionResizeMode(
                columna,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        self.verticalHeader().setDefaultSectionSize(
            24,
        )

        self.mostrar(
            [],
        )

    def mostrar(
        self,
        filas,
    ) -> None:
        """``filas``: lista de (nombre, base, tarifa, valor)."""

        filas = list(
            filas or [],
        )

        if not filas:

            self.setRowCount(
                1,
            )

            item = QTableWidgetItem(
                "No hay impuestos calculados",
            )

            item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter,
            )

            item.setForeground(
                Qt.GlobalColor.gray,
            )

            self.setItem(
                0,
                0,
                item,
            )

            self.setSpan(
                0,
                0,
                1,
                4,
            )

            return

        self.clearSpans()

        self.setRowCount(
            len(
                filas,
            ),
        )

        for fila, (nombre, base, tarifa, valor) in enumerate(
            filas,
        ):

            textos = (
                str(
                    nombre,
                ),
                formato_moneda(
                    base,
                ),
                f"{float(tarifa or 0):g} %",
                formato_moneda(
                    valor,
                ),
            )

            for columna, texto in enumerate(
                textos,
            ):

                item = QTableWidgetItem(
                    texto,
                )

                if columna:

                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter,
                    )

                self.setItem(
                    fila,
                    columna,
                    item,
                )


# =========================================================
# Caja de totales con encabezado
# =========================================================


def caja_totales(
    panel: QWidget,
    titulo: str = "Totales",
) -> QFrame:

    caja = QFrame()

    caja.setObjectName(
        "CajaTotales",
    )

    caja.setAttribute(
        Qt.WidgetAttribute.WA_StyledBackground,
        True,
    )

    layout = QVBoxLayout(
        caja,
    )

    layout.setContentsMargins(
        0,
        0,
        0,
        0,
    )

    layout.setSpacing(
        0,
    )

    encabezado = QLabel(
        titulo,
    )

    encabezado.setObjectName(
        "CajaTotalesTitulo",
    )

    layout.addWidget(
        encabezado,
    )

    layout.addWidget(
        panel,
    )

    layout.addStretch(
        1,
    )

    interno = panel.layout()

    if interno is not None:

        interno.setContentsMargins(
            12,
            6,
            12,
            8,
        )

        if isinstance(
            interno,
            QGridLayout,
        ):

            interno.setVerticalSpacing(
                4,
            )

        else:

            interno.setSpacing(
                4,
            )

    for combo in panel.findChildren(
        QWidget,
    ):

        if type(combo).__name__ == "CeldaRetencionCombo":

            combo.setMaximumHeight(
                28,
            )

    caja.setSizePolicy(
        QSizePolicy.Policy.Preferred,
        QSizePolicy.Policy.Maximum,
    )

    return caja


# =========================================================
# Utilidades de layout
# =========================================================


def contiene(
    item_layout,
    objetivo: QWidget,
) -> bool:
    """¿El item (widget o layout) contiene ``objetivo``?"""

    widget = item_layout.widget() if hasattr(
        item_layout,
        "widget",
    ) else None

    if widget is not None:

        return widget is objetivo or widget.isAncestorOf(
            objetivo,
        )

    layout = item_layout.layout() if hasattr(
        item_layout,
        "layout",
    ) else None

    if layout is None:

        return False

    for indice in range(
        layout.count(),
    ):

        if contiene(
            layout.itemAt(
                indice,
            ),
            objetivo,
        ):

            return True

    return False


def indice_en_layout(
    layout: QLayout,
    objetivo: QWidget,
) -> int:

    for indice in range(
        layout.count(),
    ):

        if contiene(
            layout.itemAt(
                indice,
            ),
            objetivo,
        ):

            return indice

    return -1


def quitar_item(
    layout: QLayout,
    indice: int,
) -> None:
    """Saca el item ``indice`` y destruye lo que quede dentro."""

    item = layout.takeAt(
        indice,
    )

    if item is None:

        return

    widget = item.widget()

    if widget is not None:

        widget.hide()

        widget.deleteLater()

        return

    sub = item.layout()

    if sub is not None:

        while sub.count():

            quitar_item(
                sub,
                0,
            )


# =========================================================
# Orden de la tecla Tab
# =========================================================


def _recolectar_foco(
    objeto,
    salida: list,
) -> None:

    from PySide6.QtWidgets import (
        QScrollArea,
        QTabWidget,
        QWidget as _QWidget,
    )

    if isinstance(
        objeto,
        QLayout,
    ):

        for indice in range(
            objeto.count(),
        ):

            item = objeto.itemAt(
                indice,
            )

            if item.widget() is not None:

                _recolectar_foco(
                    item.widget(),
                    salida,
                )

            elif item.layout() is not None:

                _recolectar_foco(
                    item.layout(),
                    salida,
                )

        return

    if not isinstance(
        objeto,
        _QWidget,
    ):

        return

    if isinstance(
        objeto,
        QTableWidget,
    ):

        for fila in range(
            objeto.rowCount(),
        ):

            for columna in range(
                objeto.columnCount(),
            ):

                if objeto.isColumnHidden(
                    columna,
                ):

                    continue

                celda = objeto.cellWidget(
                    fila,
                    columna,
                )

                if celda is not None:

                    _recolectar_foco(
                        celda,
                        salida,
                    )

        return

    if isinstance(
        objeto,
        QTabWidget,
    ):

        for indice in range(
            objeto.count(),
        ):

            _recolectar_foco(
                objeto.widget(
                    indice,
                ),
                salida,
            )

        return

    if isinstance(
        objeto,
        QScrollArea,
    ):

        if objeto.widget() is not None:

            _recolectar_foco(
                objeto.widget(),
                salida,
            )

        return

    if objeto.focusPolicy() & Qt.FocusPolicy.TabFocus:

        salida.append(
            objeto,
        )

        return

    if objeto.layout() is not None:

        _recolectar_foco(
            objeto.layout(),
            salida,
        )


def orden_tab_visual(
    raiz,
    *,
    al_final: list | None = None,
) -> list:
    """
    Ordena la tecla Tab según cómo se ven los campos (de arriba a
    abajo y de izquierda a derecha). Hace falta después de mover
    widgets a otros contenedores: Qt los manda al final de la cadena.
    """

    widgets: list = []

    _recolectar_foco(
        raiz,
        widgets,
    )

    finales = list(
        al_final or [],
    )

    widgets = [
        widget
        for widget in widgets
        if widget not in finales
    ] + finales

    for anterior, siguiente in zip(
        widgets,
        widgets[1:],
    ):

        QWidget.setTabOrder(
            anterior,
            siguiente,
        )

    return widgets


# =========================================================
# Diseño de escritorio genérico para formularios sencillos
# =========================================================


def _tomar_items(
    layout: QLayout,
) -> list:

    elementos = []

    while layout.count():

        item = layout.takeAt(
            0,
        )

        if item.widget() is not None:

            elementos.append(
                item.widget(),
            )

        elif item.layout() is not None:

            elementos.append(
                item.layout(),
            )

    return elementos


def _botones_de(
    layout: QLayout,
) -> list:

    botones = []

    for indice in range(
        layout.count(),
    ):

        widget = layout.itemAt(
            indice,
        ).widget()

        if isinstance(
            widget,
            QPushButton,
        ):

            botones.append(
                widget,
            )

    return botones


def _caja_desde_formulario(
    formulario,
    excluir: set,
) -> CajaDatos:

    from PySide6.QtWidgets import QFormLayout, QTextEdit

    caja = CajaDatos(
        "Datos del documento",
    )

    pares = []
    anchos = []

    if isinstance(
        formulario,
        QFormLayout,
    ):

        for fila in range(
            formulario.rowCount(),
        ):

            etiqueta = formulario.itemAt(
                fila,
                QFormLayout.ItemRole.LabelRole,
            )

            campo = formulario.itemAt(
                fila,
                QFormLayout.ItemRole.FieldRole,
            ) or formulario.itemAt(
                fila,
                QFormLayout.ItemRole.SpanningRole,
            )

            widget_campo = campo.widget() if campo is not None else None
            widget_etiqueta = etiqueta.widget() if etiqueta is not None else None

            if widget_campo is None or widget_campo in excluir:

                if widget_etiqueta is not None:

                    widget_etiqueta.hide()

                continue

            if isinstance(
                widget_campo,
                QTextEdit,
            ):

                anchos.append(
                    (
                        widget_etiqueta,
                        widget_campo,
                    ),
                )

            else:

                pares.append(
                    (
                        widget_etiqueta,
                        widget_campo,
                    ),
                )

    elif isinstance(
        formulario,
        QGridLayout,
    ):

        posiciones = []

        for indice in range(
            formulario.count(),
        ):

            fila, columna, _f, columnas = formulario.getItemPosition(
                indice,
            )

            posiciones.append(
                (
                    fila,
                    columna,
                    formulario.itemAt(
                        indice,
                    ).widget(),
                ),
            )

        por_fila: dict = {}

        for fila, columna, widget in posiciones:

            por_fila.setdefault(
                fila,
                {},
            )[columna] = widget

        for fila in sorted(
            por_fila,
        ):

            columnas = por_fila[fila]

            for columna in sorted(
                columnas,
            ):

                widget = columnas[columna]

                if (
                    widget is None
                    or isinstance(
                        widget,
                        QLabel,
                    )
                ):

                    continue

                etiqueta = columnas.get(
                    columna - 1,
                )

                if widget in excluir:

                    if isinstance(
                        etiqueta,
                        QLabel,
                    ):

                        etiqueta.hide()

                    continue

                pares.append(
                    (
                        etiqueta
                        if isinstance(
                            etiqueta,
                            QLabel,
                        )
                        else None,
                        widget,
                    ),
                )

    for indice, (etiqueta, campo) in enumerate(
        pares,
    ):

        fila = indice // 2
        columna = (indice % 2) * 2

        if etiqueta is not None:

            etiqueta.setObjectName(
                "CajaDocumentoEtiqueta",
            )

            caja.grid.addWidget(
                etiqueta,
                fila,
                columna,
            )

        caja.grid.addWidget(
            campo,
            fila,
            columna + 1,
        )

    fila = (len(pares) + 1) // 2

    for etiqueta, campo in anchos:

        if etiqueta is not None:

            etiqueta.setObjectName(
                "CajaDocumentoEtiqueta",
            )

            caja.grid.addWidget(
                etiqueta,
                fila,
                0,
                Qt.AlignmentFlag.AlignTop,
            )

        campo.setMaximumHeight(
            60,
        )

        caja.grid.addWidget(
            campo,
            fila,
            1,
            1,
            3,
        )

        fila += 1

    caja.grid.setColumnStretch(
        1,
        1,
    )

    caja.grid.setColumnStretch(
        3,
        1,
    )

    return caja


def _envolver_layout(
    layout: QLayout,
) -> QWidget:
    """Pasa los items de un layout suelto a un widget nuevo."""

    from PySide6.QtWidgets import QBoxLayout

    contenedor = QFrame()

    if isinstance(
        layout,
        QBoxLayout,
    ):

        nuevo = QBoxLayout(
            layout.direction(),
            contenedor,
        )

    else:

        nuevo = QHBoxLayout(
            contenedor,
        )

    nuevo.setContentsMargins(
        0,
        0,
        0,
        0,
    )

    nuevo.setSpacing(
        layout.spacing() if layout.spacing() >= 0 else 6,
    )

    while layout.count():

        item = layout.takeAt(
            0,
        )

        if item.widget() is not None:

            nuevo.addWidget(
                item.widget(),
                0,
                item.alignment(),
            )

        elif item.layout() is not None:

            interno = item.layout()

            interno.setParent(
                None,
            )

            nuevo.addLayout(
                interno,
            )

        elif item.spacerItem() is not None:

            nuevo.addStretch(
                1,
            )

    return contenedor


def _es_guardar(
    boton,
) -> bool:

    texto = boton.text().lower()

    return "guardar" in texto or "registrar" in texto


def aplicar_diseno_documento(
    pagina,
    titulo: str,
    *,
    area: str = "",
    numero: QWidget | None = None,
    tercero: QWidget | None = None,
    etiqueta_tercero: str = "Cliente",
    titulo_tercero: str = "Información del cliente",
    cartera: str = "cxc",
) -> None:
    """
    Reorganiza un formulario de documento sencillo (recibo de caja,
    egreso, documento soporte, comprobante contable…) con el mismo
    diseño de la factura: barra de título con número, barra de
    acciones arriba, cajas con marco y teclas de función.
    """

    from PySide6.QtWidgets import (
        QFormLayout,
        QMessageBox,
        QTextEdit,
    )

    from aplicacion.framework.ui.atajos import pulsar, registrar_atajos
    from aplicacion.framework.ui.card import Card
    from aplicacion.framework.ui.colores_modulo import COLORES_AREA

    layout_pagina = pagina.layout_principal

    crudos = _tomar_items(
        layout_pagina,
    )

    elementos = []
    tarjetas_viejas = []

    for elemento in crudos:

        if isinstance(
            elemento,
            Card,
        ):

            elementos.extend(
                _tomar_items(
                    elemento.contenido,
                ),
            )

            tarjetas_viejas.append(
                elemento,
            )

        else:

            elementos.append(
                elemento,
            )

    # ---- Botones de abajo -> barra de acciones ----

    botones = []

    for elemento in reversed(
        elementos,
    ):

        if isinstance(
            elemento,
            QLayout,
        ):

            encontrados = _botones_de(
                elemento,
            )

            if any(
                _es_guardar(boton)
                for boton in encontrados
            ):

                botones = encontrados

                elementos.remove(
                    elemento,
                )

                break

    hoja = Card(
        "",
    )

    hoja.setObjectName(
        "card",
    )

    hoja.layout_principal.setContentsMargins(
        0,
        0,
        0,
        10,
    )

    hoja.layout_principal.setSpacing(
        6,
    )

    hoja.contenido.setContentsMargins(
        10,
        0,
        10,
        0,
    )

    hoja.contenido.setSpacing(
        6,
    )

    color = COLORES_AREA.get(
        area,
        "#1E3A5F",
    )

    barra_titulo = BarraTituloDocumento(
        titulo,
        color,
    )

    if numero is not None:

        if isinstance(
            numero,
            QLabel,
        ) or getattr(
            numero,
            "isReadOnly",
            lambda: False,
        )():

            numero.setFixedWidth(
                140,
            )

            barra_titulo.set_numero_widget(
                numero,
            )

        else:

            barra_titulo.caja_numero.hide()

            numero = None

    else:

        barra_titulo.caja_numero.hide()

    hoja.layout_principal.insertWidget(
        0,
        barra_titulo,
    )

    barra_acciones = BarraAccionesDocumento()

    hoja.layout_principal.insertWidget(
        1,
        barra_acciones,
    )

    boton_guardar = None
    boton_cerrar = None

    for boton in botones:

        texto = boton.text().lower()

        if _es_guardar(boton) and boton_guardar is None:

            boton_guardar = boton

    if boton_guardar is not None:

        boton_guardar.setObjectName(
            "BotonPrimario",
        )

        barra_acciones.agregar(
            boton_guardar,
            "guardar",
            "F10",
        )

    for boton in botones:

        if boton is boton_guardar:

            continue

        texto = boton.text().lower()

        if "cancelar" in texto or "cerrar" in texto:

            boton_cerrar = boton

            boton.setText(
                "Cerrar",
            )

            barra_acciones.agregar_al_final(
                boton,
                "cerrar",
                "Esc",
            )

        else:

            icono = (
                "imprimir"
                if "imprim" in texto
                else "pdf"
                if "pdf" in texto
                else None
            )

            barra_acciones.agregar(
                boton,
                icono,
            )

    # ---- Cabecera -> cajas con marco ----

    excluir = set()

    if numero is not None:

        excluir.add(
            numero,
        )

    if tercero is not None:

        excluir.add(
            tercero,
        )

    indice_cabecera = None

    for indice, elemento in enumerate(
        elementos,
    ):

        formulario = None

        if isinstance(
            elemento,
            (
                QFormLayout,
                QGridLayout,
            ),
        ):

            formulario = elemento

        elif isinstance(
            elemento,
            QWidget,
        ) and isinstance(
            elemento.layout(),
            (
                QFormLayout,
                QGridLayout,
            ),
        ):

            formulario = elemento.layout()

        if formulario is not None:

            indice_cabecera = indice

            break

    panel_tercero = None

    if indice_cabecera is not None:

        cabecera = elementos[indice_cabecera]

        formulario = (
            cabecera
            if isinstance(
                cabecera,
                QLayout,
            )
            else cabecera.layout()
        )

        caja_documento = _caja_desde_formulario(
            formulario,
            excluir,
        )

        fila_cajas = QWidget()

        layout_cajas = QHBoxLayout(
            fila_cajas,
        )

        layout_cajas.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout_cajas.setSpacing(
            8,
        )

        if tercero is not None:

            if tercero.minimumHeight() > 28:

                tercero.setFixedHeight(
                    28,
                )

            panel_tercero = PanelTercero(
                titulo_tercero,
                tercero,
                etiqueta=etiqueta_tercero,
                cartera=cartera,
            )

            layout_cajas.addWidget(
                panel_tercero,
                1,
            )

            valor = getattr(
                tercero,
                "valor",
                lambda: None,
            )()

            if valor:

                try:

                    panel_tercero.mostrar_tercero(
                        int(
                            valor,
                        ),
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    pass

        layout_cajas.addWidget(
            caja_documento,
            1,
        )

        fila_cajas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

        if isinstance(
            cabecera,
            QWidget,
        ):

            cabecera.hide()

            cabecera.deleteLater()

        elementos[indice_cabecera] = fila_cajas

    # ---- Resto, en el mismo orden ----

    boton_agregar = None

    for elemento in elementos:

        if isinstance(
            elemento,
            QLayout,
        ):

            con_agregar = [
                boton
                for boton in _botones_de(
                    elemento,
                )
                if "agregar" in boton.text().lower()
            ]

            widget = _envolver_layout(
                elemento,
            )

            if con_agregar:

                boton_agregar = con_agregar[0]

                boton_agregar.setObjectName(
                    "BotonAgregarLinea",
                )

                widget.setObjectName(
                    "DocumentoFilaTotales",
                )

                widget.layout().setContentsMargins(
                    4,
                    2,
                    10,
                    2,
                )

            elemento = widget

        if isinstance(
            elemento,
            QTableWidget,
        ):

            hoja.contenido.addWidget(
                elemento,
                1,
            )

            continue

        if isinstance(
            elemento,
            QTextEdit,
        ):

            elemento.setMaximumHeight(
                90,
            )

        hoja.contenido.addWidget(
            elemento,
        )

    hay_tabla = any(
        isinstance(
            elemento,
            QTableWidget,
        )
        and not elemento.isHidden()
        for elemento in elementos
    )

    if not hay_tabla:

        # Sin detalle que crezca, el espacio sobrante va al final
        # (si no, lo tomaba la barra de título).
        hoja.contenido.addStretch(
            1,
        )

    for barra in (
        barra_titulo,
        barra_acciones,
    ):

        barra.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

    layout_pagina.setContentsMargins(
        8,
        8,
        8,
        8,
    )

    layout_pagina.addWidget(
        hoja,
    )

    for tarjeta in tarjetas_viejas:

        tarjeta.hide()

        tarjeta.deleteLater()

    pagina.barra_titulo = barra_titulo
    pagina.barra_acciones = barra_acciones
    pagina.panel_tercero = panel_tercero

    # ---- Teclas ----

    def cerrar_con_escape():

        respuesta = QMessageBox.question(
            pagina,
            "Cerrar",
            "¿Cerrar el documento sin guardar los cambios?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if respuesta != QMessageBox.Yes:

            return

        if boton_cerrar is not None:

            boton_cerrar.click()

        elif hasattr(
            pagina,
            "cerrar",
        ):

            pagina.cerrar.emit()

    puede_cerrar = boton_cerrar is not None or hasattr(
        pagina,
        "cerrar",
    )

    atajos = (
        [
            ("Escape", cerrar_con_escape),
        ]
        if puede_cerrar
        else []
    )

    teclas = []

    if boton_guardar is not None:

        atajos.append(
            (
                (
                    "Ctrl+S",
                    "F10",
                ),
                lambda: pulsar(boton_guardar),
            ),
        )

        teclas.append(
            ("F10", "Guardar", lambda: pulsar(boton_guardar)),
        )

    boton_tercero = getattr(
        tercero,
        "btn",
        None,
    )

    if boton_tercero is not None:

        atajos.append(
            ("F3", lambda: pulsar(boton_tercero)),
        )

        teclas.append(
            ("F3", etiqueta_tercero, lambda: pulsar(boton_tercero)),
        )

        boton_tercero.setToolTip(
            f"Buscar {etiqueta_tercero.lower()} (F3)",
        )

    if boton_agregar is not None:

        atajos.append(
            ("Ctrl+L", lambda: pulsar(boton_agregar)),
        )

        teclas.append(
            ("Ctrl+L", "Agregar línea", lambda: pulsar(boton_agregar)),
        )

    teclas.append(
        ("Tab", "Siguiente campo", lambda: pagina.focusNextChild()),
    )

    if puede_cerrar:

        teclas.append(
            ("Esc", "Cerrar", cerrar_con_escape),
        )

    registrar_atajos(
        pagina,
        atajos,
    )

    pagina.teclas_contexto = lambda: list(
        teclas,
    )

    orden_tab_visual(
        hoja.contenido,
        al_final=[
            boton
            for boton in (
                boton_guardar,
                boton_cerrar,
            )
            if boton is not None
        ],
    )
