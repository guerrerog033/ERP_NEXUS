from PySide6.QtCore import QDate, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from aplicacion.recursos.estilos.estilos import Estilos
from aplicacion.recursos.ui.botones import Botones


class MaestroToolbar(QWidget):
    """
    Toolbar unificada del maestro.

    Fila 1 (barra de herramientas): Nuevo, Editar, Consultar,
    Eliminar | Actualizar, Imprimir, Excel, PDF | Más.

    Fila 2 (barra de búsqueda, estilo Sysplus / Magister):
    "Buscar por" (todas las columnas o una en particular), el texto a
    buscar y, en los listados con fecha, el rango "Desde / Hasta".
    """

    buscar = Signal(str)
    actualizar = Signal()
    excel = Signal()
    pdf = Signal()
    imprimir = Signal()

    # Rango de fechas (QDate, QDate) y limpiar rango.
    fechas_aplicadas = Signal(object, object)
    fechas_limpiadas = Signal()

    # Cambió la columna de "Buscar por" ("" = todas).
    columna_busqueda_cambiada = Signal(str)

    def __init__(
        self,
    ):

        super().__init__()

        self.setObjectName(
            "DataGridToolbar",
        )

        self._crear_interfaz()

    # -----------------------------------------------------

    def _boton_herramienta(
        self,
        texto: str,
        icono: str,
        accion,
    ) -> QToolButton:

        from aplicacion.framework.ui.iconos import icono_accion

        boton = QToolButton()

        boton.setObjectName(
            "BotonBarraLista",
        )

        boton.setText(
            texto,
        )

        boton.setIcon(
            icono_accion(
                icono,
                "#334155",
                18,
            ),
        )

        boton.setIconSize(
            QSize(
                18,
                18,
            ),
        )

        boton.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon,
        )

        boton.setAutoRaise(
            True,
        )

        boton.setCursor(
            Qt.PointingHandCursor,
        )

        boton.clicked.connect(
            lambda _=False: accion.trigger(),
        )

        return boton

    def _separador(
        self,
    ) -> QFrame:

        linea = QFrame()

        linea.setObjectName(
            "ToolbarSeparador",
        )

        linea.setFrameShape(
            QFrame.VLine,
        )

        linea.setFixedWidth(
            1,
        )

        linea.setFixedHeight(
            24,
        )

        return linea

    def _crear_interfaz(
        self,
    ) -> None:

        principal = QVBoxLayout(
            self,
        )

        principal.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        principal.setSpacing(
            4,
        )

        # ---------------- Fila 1: herramientas ----------------

        self.barra_herramientas = QFrame()

        self.barra_herramientas.setObjectName(
            "BarraHerramientasLista",
        )

        layout = QHBoxLayout(
            self.barra_herramientas,
        )

        layout.setContentsMargins(
            4,
            3,
            4,
            3,
        )

        layout.setSpacing(
            4,
        )

        self.btn_nuevo = Botones.nuevo()
        self.btn_editar = Botones.editar()
        self.btn_consultar = Botones.secundario(
            "Consultar",
        )
        self.btn_eliminar = Botones.eliminar()

        from aplicacion.framework.ui.iconos import icono_accion

        self.btn_consultar.setIcon(
            icono_accion(
                "consultar",
                "#334155",
                18,
            ),
        )

        for boton in (
            self.btn_nuevo,
            self.btn_editar,
            self.btn_consultar,
            self.btn_eliminar,
        ):

            boton.setMinimumHeight(
                28,
            )

            boton.setMinimumWidth(
                92,
            )

            layout.addWidget(
                boton,
            )

        menu = QMenu(
            self,
        )

        self.accion_actualizar = menu.addAction(
            "Actualizar",
        )

        self.accion_excel = menu.addAction(
            "Exportar Excel",
        )

        self.accion_pdf = menu.addAction(
            "Exportar PDF",
        )

        self.accion_imprimir = menu.addAction(
            "Imprimir",
        )

        self.accion_actualizar.triggered.connect(
            self.actualizar.emit,
        )

        self.accion_excel.triggered.connect(
            self.excel.emit,
        )

        self.accion_pdf.triggered.connect(
            self.pdf.emit,
        )

        self.accion_imprimir.triggered.connect(
            self.imprimir.emit,
        )

        layout.addWidget(
            self._separador(),
        )

        self.btn_herr_actualizar = self._boton_herramienta(
            "Actualizar",
            "actualizar",
            self.accion_actualizar,
        )

        self.btn_herr_imprimir = self._boton_herramienta(
            "Imprimir",
            "imprimir",
            self.accion_imprimir,
        )

        self.btn_herr_excel = self._boton_herramienta(
            "Excel",
            "excel",
            self.accion_excel,
        )

        self.btn_herr_pdf = self._boton_herramienta(
            "PDF",
            "pdf",
            self.accion_pdf,
        )

        self.btn_herr_actualizar.setToolTip(
            "Actualizar (F5)",
        )

        self.btn_herr_imprimir.setToolTip(
            "Imprimir listado (Ctrl+P)",
        )

        for boton in (
            self.btn_herr_actualizar,
            self.btn_herr_imprimir,
            self.btn_herr_excel,
            self.btn_herr_pdf,
        ):

            layout.addWidget(
                boton,
            )

        self.btn_mas = QToolButton()

        self.btn_mas.setObjectName(
            "MaestroToolbarMas",
        )

        self.btn_mas.setText(
            "Más",
        )

        self.btn_mas.setPopupMode(
            QToolButton.InstantPopup,
        )

        self.btn_mas.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon,
        )

        self.btn_mas.setMinimumHeight(
            28,
        )

        self.btn_mas.setMenu(
            menu,
        )

        layout.addWidget(
            self._separador(),
        )

        layout.addWidget(
            self.btn_mas,
        )

        layout.addStretch(
            1,
        )

        principal.addWidget(
            self.barra_herramientas,
        )

        # ---------------- Fila 2: búsqueda ----------------

        self.barra_busqueda = QFrame()

        self.barra_busqueda.setObjectName(
            "BarraBusquedaLista",
        )

        busqueda = QHBoxLayout(
            self.barra_busqueda,
        )

        busqueda.setContentsMargins(
            8,
            4,
            8,
            4,
        )

        busqueda.setSpacing(
            6,
        )

        lbl_buscar_por = QLabel(
            "Buscar por:",
        )

        lbl_buscar_por.setObjectName(
            "EtiquetaBusqueda",
        )

        self.cmb_buscar_por = QComboBox()

        self.cmb_buscar_por.setObjectName(
            "ComboBuscarPor",
        )

        self.cmb_buscar_por.addItem(
            "Todos los campos",
            "",
        )

        self.cmb_buscar_por.setMinimumWidth(
            150,
        )

        self.cmb_buscar_por.currentIndexChanged.connect(
            lambda _i: self.columna_busqueda_cambiada.emit(
                self.columna_busqueda(),
            ),
        )

        self.txt_buscar = QLineEdit()

        self.txt_buscar.setPlaceholderText(
            "Buscar...",
        )

        self.txt_buscar.setMinimumHeight(
            28,
        )

        self.txt_buscar.setMinimumWidth(
            220,
        )

        Estilos.line_edit(
            self.txt_buscar,
        )

        self.txt_buscar.setClearButtonEnabled(
            True,
        )

        self.txt_buscar.textChanged.connect(
            self.buscar.emit,
        )

        busqueda.addWidget(
            lbl_buscar_por,
        )

        busqueda.addWidget(
            self.cmb_buscar_por,
        )

        busqueda.addWidget(
            self.txt_buscar,
            1,
        )

        # Rango de fechas (oculto hasta que el listado lo active).
        self.panel_fechas = QWidget()

        self.panel_fechas.setObjectName(
            "PanelFechasLista",
        )

        fechas = QHBoxLayout(
            self.panel_fechas,
        )

        fechas.setContentsMargins(
            10,
            0,
            0,
            0,
        )

        fechas.setSpacing(
            6,
        )

        hoy = QDate.currentDate()

        self.fecha_desde = QDateEdit(
            QDate(
                hoy.year(),
                hoy.month(),
                1,
            ),
        )

        self.fecha_hasta = QDateEdit(
            hoy,
        )

        for editor in (
            self.fecha_desde,
            self.fecha_hasta,
        ):

            editor.setCalendarPopup(
                True,
            )

            editor.setDisplayFormat(
                "dd/MM/yyyy",
            )

            editor.setMinimumWidth(
                110,
            )

        self.btn_filtrar_fechas = QPushButton(
            "Filtrar",
        )

        self.btn_filtrar_fechas.setObjectName(
            "BotonSecundario",
        )

        self.btn_quitar_fechas = QPushButton(
            "Todas",
        )

        self.btn_quitar_fechas.setObjectName(
            "BotonSecundario",
        )

        self.btn_quitar_fechas.setToolTip(
            "Ver todas las fechas",
        )

        self.btn_filtrar_fechas.clicked.connect(
            self._emitir_fechas,
        )

        self.btn_quitar_fechas.clicked.connect(
            self.fechas_limpiadas.emit,
        )

        fechas.addWidget(
            QLabel(
                "Desde:",
            ),
        )

        fechas.addWidget(
            self.fecha_desde,
        )

        fechas.addWidget(
            QLabel(
                "Hasta:",
            ),
        )

        fechas.addWidget(
            self.fecha_hasta,
        )

        fechas.addWidget(
            self.btn_filtrar_fechas,
        )

        fechas.addWidget(
            self.btn_quitar_fechas,
        )

        self.panel_fechas.setVisible(
            False,
        )

        busqueda.addWidget(
            self.panel_fechas,
        )

        principal.addWidget(
            self.barra_busqueda,
        )

        self.btn_actualizar = self.accion_actualizar
        self.btn_excel = self.accion_excel
        self.btn_pdf = self.accion_pdf
        self.btn_imprimir = self.accion_imprimir

    # -----------------------------------------------------
    # Configuración desde el maestro
    # -----------------------------------------------------

    def configurar_columnas_busqueda(
        self,
        columnas,
    ) -> None:
        """``columnas``: lista de (nombre, etiqueta)."""

        self.cmb_buscar_por.blockSignals(
            True,
        )

        self.cmb_buscar_por.clear()

        self.cmb_buscar_por.addItem(
            "Todos los campos",
            "",
        )

        for nombre, etiqueta in columnas:

            self.cmb_buscar_por.addItem(
                etiqueta,
                nombre,
            )

        self.cmb_buscar_por.blockSignals(
            False,
        )

    def columna_busqueda(
        self,
    ) -> str:

        return self.cmb_buscar_por.currentData() or ""

    def habilitar_fechas(
        self,
        habilitado: bool = True,
    ) -> None:

        self.panel_fechas.setVisible(
            habilitado,
        )

    def _emitir_fechas(
        self,
    ) -> None:

        desde = self.fecha_desde.date()
        hasta = self.fecha_hasta.date()

        if desde > hasta:

            desde, hasta = hasta, desde

        self.fechas_aplicadas.emit(
            desde,
            hasta,
        )


Toolbar = MaestroToolbar
