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
