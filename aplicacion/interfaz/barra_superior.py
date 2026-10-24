"""
Cabecera de la ventana principal: barra de herramientas con accesos
rápidos a los módulos (estilo Sysplus / Siigo Pyme) y, a la derecha,
los datos de la sesión: empresa, fecha de trabajo, usuario y alertas.
"""

from datetime import datetime

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QToolButton,
    QWidget,
)

from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss

# (módulo, texto, ícono, ayuda) — accesos de la barra de herramientas.
ACCESOS_RAPIDOS = (
    ("Inicio", "Inicio", "inicio", "Pantalla de inicio"),
    ("FacturasVenta", "Facturar", "ventas", "Facturas de venta"),
    ("Cotizaciones", "Cotizar", "ventas", "Cotizaciones"),
    ("POSVenta", "POS", "pos", "Punto de venta"),
    ("Compras", "Compras", "compras", "Compras y gastos"),
    ("Clientes", "Clientes", "terceros", "Clientes"),
    ("Productos", "Productos", "productos", "Productos y servicios"),
    ("RecibosCaja", "Recaudos", "bancos", "Recibos de caja"),
    ("Cartera", "Cartera", "cartera", "Cartera"),
    ("Inventarios", "Inventario", "inventarios", "Inventarios"),
    ("Contabilidad", "Contable", "contabilidad", "Contabilidad"),
    ("Reportes", "Informes", "reportes", "Reportes"),
)

SEPARAR_DESPUES = {
    "Inicio",
    "POSVenta",
    "Productos",
    "Contabilidad",
}


class BarraSuperior(QWidget):

    cerrar_sesion = Signal()
    busqueda_solicitada = Signal(str)
    modulo_solicitado = Signal(str)

    def __init__(self, usuario):

        super().__init__()

        self.usuario = usuario
        self._notificaciones: list[str] = []

        self.setObjectName("BarraSuperior")
        habilitar_fondo_qss(self)
        self.setFixedHeight(66)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 10, 3)
        layout.setSpacing(2)

        self._crear_accesos(layout)

        layout.addStretch(1)

        layout.addWidget(self._crear_panel_sesion(usuario))

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._actualizar_fecha)
        self._timer.start(60000)

        self._actualizar_menu_notificaciones()

    # -----------------------------------------------------
    # Barra de herramientas
    # -----------------------------------------------------

    def _crear_accesos(self, layout) -> None:

        from aplicacion.framework.menu_manifest import modulo_accesible
        from aplicacion.framework.ui.colores_modulo import COLORES_AREA
        from aplicacion.framework.ui.iconos import icono_modulo

        self.botones_acceso: dict[str, QToolButton] = {}

        for modulo_id, texto, icono, ayuda in ACCESOS_RAPIDOS:

            if modulo_id != "Inicio" and not modulo_accesible(modulo_id):
                continue

            boton = QToolButton()
            boton.setObjectName("BotonHerramienta")
            boton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            boton.setIcon(
                icono_modulo(icono, COLORES_AREA.get(icono, "#334155"), 26),
            )
            boton.setIconSize(QSize(26, 26))
            boton.setText(texto)
            boton.setToolTip(ayuda)
            boton.setAutoRaise(True)
            boton.setFocusPolicy(Qt.NoFocus)
            boton.setCursor(Qt.PointingHandCursor)
            boton.clicked.connect(
                lambda _=False, m=modulo_id: self.modulo_solicitado.emit(m),
            )

            self.botones_acceso[modulo_id] = boton
            layout.addWidget(boton)

            if modulo_id in SEPARAR_DESPUES:
                layout.addWidget(self._separador())

    def _separador(self) -> QFrame:

        linea = QFrame()
        linea.setObjectName("BarraHerramientasSeparador")
        linea.setFrameShape(QFrame.VLine)
        linea.setFixedWidth(1)
        linea.setFixedHeight(40)
        return linea

    # -----------------------------------------------------
    # Panel de sesión
    # -----------------------------------------------------

    def _crear_panel_sesion(self, usuario) -> QFrame:

        from aplicacion.framework.ui.iconos import icono_modulo
        from aplicacion.nucleo.permisos import Permisos

        empresa = Configuracion.obtener("empresa", "nombre") or "Empresa"

        self.lbl_empresa = QLabel(empresa.upper())
        self.lbl_empresa.setObjectName("BarraSuperiorTitulo")
        self.lbl_empresa.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.lbl_fecha_trabajo = QLabel("Fecha de trabajo:")
        self.lbl_fecha_trabajo.setObjectName("BarraSuperiorEtiqueta")

        self.lbl_fecha = QLabel()
        self.lbl_fecha.setObjectName("BarraSuperiorFecha")
        self._actualizar_fecha()

        self.txt_busqueda = QLineEdit()
        self.txt_busqueda.setObjectName("BarraSuperiorBusqueda")
        self.txt_busqueda.setPlaceholderText("Buscar módulo (Ctrl+K)...")
        self.txt_busqueda.setClearButtonEnabled(True)
        self.txt_busqueda.setFixedWidth(220)
        self.txt_busqueda.returnPressed.connect(self._emitir_busqueda)

        nombre_erp = Configuracion.obtener("erp", "nombre") or "ERP NEXUS"
        self.lbl_producto = QLabel(nombre_erp)
        self.lbl_producto.setObjectName("BarraSuperiorSubtitulo")

        self.btn_notificaciones = QToolButton()
        self.btn_notificaciones.setObjectName("BarraSuperiorNotificaciones")
        self.btn_notificaciones.setPopupMode(QToolButton.InstantPopup)
        self.btn_notificaciones.setText("Alertas")
        self.btn_notificaciones.setCursor(Qt.PointingHandCursor)
        self.btn_notificaciones.setFocusPolicy(Qt.NoFocus)

        self.menu_notificaciones = QMenu(self)
        self.btn_notificaciones.setMenu(self.menu_notificaciones)

        self.lbl_badge = QLabel("0", self.btn_notificaciones)
        self.lbl_badge.setObjectName("BarraSuperiorBadge")
        self.lbl_badge.setAlignment(Qt.AlignCenter)
        self.lbl_badge.hide()

        self.btn_usuario = QToolButton()
        self.btn_usuario.setObjectName("BarraSuperiorUsuario")
        self.btn_usuario.setPopupMode(QToolButton.InstantPopup)
        self.btn_usuario.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.btn_usuario.setIcon(icono_modulo("terceros", "#FFFFFF", 16))
        self.btn_usuario.setText(usuario.nombre)
        self.btn_usuario.setCursor(Qt.PointingHandCursor)
        self.btn_usuario.setFocusPolicy(Qt.NoFocus)

        menu_usuario = QMenu(self)
        menu_usuario.addAction(f"Usuario: {usuario.nombre}").setEnabled(False)
        menu_usuario.addAction(
            f"Rol: {Permisos.rol_codigo() or 'sin rol'}",
        ).setEnabled(False)
        menu_usuario.addSeparator()
        menu_usuario.addAction("Cerrar sesión", self.cerrar_sesion.emit)
        self.btn_usuario.setMenu(menu_usuario)

        panel = QFrame()
        panel.setObjectName("PanelSesion")

        rejilla = QGridLayout(panel)
        rejilla.setContentsMargins(12, 4, 8, 4)
        rejilla.setHorizontalSpacing(8)
        rejilla.setVerticalSpacing(3)

        fila_fecha = QHBoxLayout()
        fila_fecha.setSpacing(6)
        fila_fecha.addWidget(self.lbl_fecha_trabajo)
        fila_fecha.addWidget(self.lbl_fecha)
        fila_fecha.addStretch(1)

        rejilla.addWidget(self.lbl_empresa, 0, 0)
        rejilla.addLayout(fila_fecha, 1, 0)
        rejilla.addWidget(self.btn_notificaciones, 0, 1)
        rejilla.addWidget(self.btn_usuario, 0, 2)
        rejilla.addWidget(self.txt_busqueda, 1, 1, 1, 2)

        return panel

    def enfocar_busqueda(
        self,
    ) -> None:

        self.txt_busqueda.setFocus(
            Qt.ShortcutFocusReason,
        )

        self.txt_busqueda.selectAll()

    def agregar_notificacion(
        self,
        mensaje: str,
    ) -> None:

        texto = str(
            mensaje or "",
        ).strip()

        if not texto:

            return

        self._notificaciones.insert(
            0,
            texto,
        )

        self._notificaciones = self._notificaciones[
            :20
        ]

        self._actualizar_menu_notificaciones()

    def limpiar_notificaciones(
        self,
    ) -> None:

        self._notificaciones.clear()

        self._actualizar_menu_notificaciones()

    def _actualizar_menu_notificaciones(
        self,
    ) -> None:

        self.menu_notificaciones.clear()

        if not self._notificaciones:

            accion = self.menu_notificaciones.addAction(
                "Sin alertas pendientes",
            )

            accion.setEnabled(
                False,
            )

            self.lbl_badge.hide()

            return

        for mensaje in self._notificaciones:

            self.menu_notificaciones.addAction(
                mensaje,
            )

        self.menu_notificaciones.addSeparator()

        self.menu_notificaciones.addAction(
            "Marcar todas como leídas",
            self.limpiar_notificaciones,
        )

        cantidad = len(
            self._notificaciones,
        )

        self.lbl_badge.setText(
            str(
                min(
                    cantidad,
                    9,
                )
            )
            + (
                "+"
                if cantidad > 9
                else ""
            ),
        )

        self.lbl_badge.show()

    def _actualizar_fecha(
        self,
    ) -> None:

        self.lbl_fecha.setText(
            datetime.now().strftime(
                "%d/%m/%Y",
            ),
        )

    def _emitir_busqueda(
        self,
    ) -> None:

        self.busqueda_solicitada.emit(
            self.txt_busqueda.text().strip(),
        )

        self.txt_busqueda.clear()

    def resizeEvent(
        self,
        event,
    ) -> None:

        super().resizeEvent(
            event,
        )

        if self.lbl_badge.isVisible():

            self.lbl_badge.move(
                self.btn_notificaciones.width()
                - 18,
                4,
            )
