from datetime import datetime

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QToolButton,
    QWidget,
)

from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss
from aplicacion.recursos.ui.recursos import Recursos


class BarraSuperior(QWidget):

    cerrar_sesion = Signal()
    busqueda_solicitada = Signal(str)

    def __init__(
        self,
        usuario,
    ):

        super().__init__()

        self.usuario = usuario
        self._notificaciones: list[str] = []

        self.setObjectName(
            "BarraSuperior",
        )

        habilitar_fondo_qss(
            self,
        )

        self.setFixedHeight(
            46,
        )

        layout = QHBoxLayout(
            self,
        )

        layout.setContentsMargins(
            12,
            0,
            12,
            0,
        )

        layout.setSpacing(
            12,
        )

        empresa = (
            Configuracion.obtener(
                "empresa",
                "nombre",
            )
            or "Empresa"
        )

        self.lbl_empresa = QLabel(
            empresa.upper(),
        )

        self.lbl_empresa.setObjectName(
            "BarraSuperiorTitulo",
        )

        self.lbl_empresa.setFont(
            QFont(
                "Segoe UI",
                11,
                QFont.Bold,
            ),
        )

        separador = QFrame()

        separador.setObjectName(
            "BarraSuperiorSeparador",
        )

        separador.setFrameShape(
            QFrame.VLine,
        )

        separador.setFixedWidth(
            1,
        )

        self.lbl_fecha_trabajo = QLabel(
            "Fecha trabajo:",
        )

        self.lbl_fecha_trabajo.setObjectName(
            "BarraSuperiorEtiqueta",
        )

        self.lbl_fecha = QLabel()

        self.lbl_fecha.setObjectName(
            "BarraSuperiorFecha",
        )

        self.lbl_fecha.setMinimumWidth(
            78,
        )

        self._actualizar_fecha()

        self.txt_busqueda = QLineEdit()

        self.txt_busqueda.setObjectName(
            "BarraSuperiorBusqueda",
        )

        self.txt_busqueda.setPlaceholderText(
            "Buscar módulo (Ctrl+K)...",
        )

        self.txt_busqueda.setClearButtonEnabled(
            True,
        )

        self.txt_busqueda.setMinimumWidth(
            200,
        )

        self.txt_busqueda.setMaximumWidth(
            320,
        )

        self.txt_busqueda.returnPressed.connect(
            self._emitir_busqueda,
        )

        nombre_erp = (
            Configuracion.obtener(
                "erp",
                "nombre",
            )
            or "ERP NEXUS"
        )

        self.lbl_producto = QLabel(
            nombre_erp,
        )

        self.lbl_producto.setObjectName(
            "BarraSuperiorSubtitulo",
        )

        self.lbl_producto.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter,
        )

        self.btn_notificaciones = QToolButton()

        self.btn_notificaciones.setObjectName(
            "BarraSuperiorNotificaciones",
        )

        self.btn_notificaciones.setPopupMode(
            QToolButton.InstantPopup,
        )

        self.btn_notificaciones.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon,
        )

        self.btn_notificaciones.setText(
            "Alertas",
        )

        self.btn_notificaciones.setCursor(
            Qt.PointingHandCursor,
        )

        self.menu_notificaciones = QMenu(
            self,
        )

        self.btn_notificaciones.setMenu(
            self.menu_notificaciones,
        )

        self.lbl_badge = QLabel(
            "0",
            self.btn_notificaciones,
        )

        self.lbl_badge.setObjectName(
            "BarraSuperiorBadge",
        )

        self.lbl_badge.setAlignment(
            Qt.AlignCenter,
        )

        self.lbl_badge.hide()

        self.btn_usuario = QToolButton()

        self.btn_usuario.setObjectName(
            "BarraSuperiorUsuario",
        )

        self.btn_usuario.setPopupMode(
            QToolButton.InstantPopup,
        )

        self.btn_usuario.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon,
        )

        self.btn_usuario.setIcon(
            Recursos.icono_desde_emoji(
                "👤",
                18,
            ),
        )

        self.btn_usuario.setText(
            usuario.nombre,
        )

        self.btn_usuario.setCursor(
            Qt.PointingHandCursor,
        )

        menu_usuario = QMenu(
            self,
        )

        menu_usuario.addAction(
            f"Usuario: {usuario.nombre}",
        ).setEnabled(
            False,
        )

        from aplicacion.nucleo.permisos import (
            Permisos,
        )

        rol_etiqueta = (
            Permisos.rol_codigo()
            or "sin rol"
        )

        menu_usuario.addAction(
            f"Rol: {rol_etiqueta}",
        ).setEnabled(
            False,
        )

        menu_usuario.addSeparator()

        menu_usuario.addAction(
            "Cerrar sesión",
            self.cerrar_sesion.emit,
        )

        self.btn_usuario.setMenu(
            menu_usuario,
        )

        layout.addWidget(
            self.lbl_empresa,
        )

        layout.addWidget(
            separador,
        )

        layout.addWidget(
            self.lbl_fecha_trabajo,
        )

        layout.addWidget(
            self.lbl_fecha,
        )

        layout.addWidget(
            self.txt_busqueda,
            1,
        )

        layout.addWidget(
            self.lbl_producto,
        )

        layout.addWidget(
            self.btn_notificaciones,
        )

        layout.addWidget(
            self.btn_usuario,
        )

        self._timer = QTimer(
            self,
        )

        self._timer.timeout.connect(
            self._actualizar_fecha,
        )

        self._timer.start(
            60000,
        )

        self._actualizar_menu_notificaciones()

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
