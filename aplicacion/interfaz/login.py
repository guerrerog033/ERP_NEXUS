from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QFrame,
    QHBoxLayout,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from aplicacion.interfaz.dialogo_licencia import (
    DialogoActivacionLicencia,
)
from aplicacion.interfaz.fondo_login import (
    pintar_fondo_login,
)
from aplicacion.interfaz.trabajo_login import TrabajoInicioSesion
from aplicacion.recursos.estilos.tema import (
    habilitar_fondo_qss,
)


class Login(QWidget):

    _TIMEOUT_MS = 60000

    sesion_iniciada = Signal(
        object,
    )

    def __init__(
        self,
        *,
        embebido: bool = False,
    ):

        super().__init__()

        self._embebido = embebido
        self._conectando = False
        self._hilo = None
        self._trabajo = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._tiempo_agotado)

        self.setObjectName("Login")

        habilitar_fondo_qss(
            self,
        )

        layout_raiz = QVBoxLayout(
            self,
        )

        layout_raiz.setContentsMargins(
            48,
            40,
            48,
            40,
        )

        self.setStyleSheet(
            """
            QWidget#Login,
            QWidget#LoginMarcaPanel {
                background: transparent;
            }
            QFrame#LoginPanel {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8FBFF,
                    stop:0.55 #EEF4FC,
                    stop:1 #E3EDF8
                );
                border: 1px solid #9BB8D8;
                border-radius: 18px;
            }
            QFrame#LoginPanelCabecera {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1B4F8A,
                    stop:0.55 #2569A8,
                    stop:1 #3A7BC5
                );
                border-top-left-radius: 17px;
                border-top-right-radius: 17px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.18);
            }
            QWidget#LoginPanelCuerpo {
                background: transparent;
            }
            QLabel#LoginTitulo {
                font-size: 28px;
                font-weight: 700;
                color: #FFFFFF;
            }
            QLabel#LoginMarcaTitulo {
                font-size: 42px;
                font-weight: 700;
                color: #FFFFFF;
            }
            QLabel#LoginMarcaTexto {
                font-size: 13pt;
                color: #E8F4FF;
                line-height: 1.5;
            }
            QLabel#LoginDestacadoMarca {
                background: rgba(255, 255, 255, 0.12);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.28);
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 8pt;
                font-weight: 600;
            }
            QLabel#LoginSubtitulo {
                font-size: 15pt;
                font-weight: 700;
                color: #FFFFFF;
            }
            QLabel#LoginCabeceraDetalle {
                font-size: 9pt;
                color: rgba(255, 255, 255, 0.82);
            }
            QLabel#LoginModuloChip {
                background: rgba(27, 79, 138, 0.08);
                color: #1B4F8A;
                border: 1px solid #C5D8EB;
                border-radius: 10px;
                padding: 4px 8px;
                font-size: 8pt;
                font-weight: 600;
            }
            QLabel#LoginEtiquetaCampo {
                font-size: 10pt;
                font-weight: 600;
                color: #1B4F8A;
                margin-top: 4px;
            }
            QLineEdit#LoginCampo {
                background: #FFFFFF;
                border: 1px solid #AFC6DE;
                border-radius: 8px;
                padding: 10px 12px;
                min-height: 20px;
                font-size: 11pt;
                color: #1A3A5C;
            }
            QLineEdit#LoginCampo:focus {
                border: 2px solid #3A7BC5;
                background: #FFFFFF;
            }
            QPushButton#LoginBoton {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A8BD0,
                    stop:1 #1B4F8A
                );
                color: white;
                font-size: 11pt;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                padding: 12px;
                min-height: 24px;
            }
            QPushButton#LoginBoton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5A9BE0,
                    stop:1 #245F96
                );
            }
            QPushButton#LoginBoton:disabled {
                background: #A8C0D8;
                color: #E8F0F8;
            }
            """
        )

        if not embebido:

            self.setWindowTitle(
                "ERP NEXUS - Inicio de sesión",
            )

            self.resize(
                960,
                640,
            )

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        if embebido:

            fila_central = QHBoxLayout()

            fila_central.setSpacing(
                64,
            )

            marca = QVBoxLayout()

            marca.setSpacing(
                12,
            )

            marca_titulo = QLabel(
                "ERP NEXUS",
            )

            marca_titulo.setObjectName(
                "LoginMarcaTitulo",
            )

            marca_texto = QLabel(
                "Gestión empresarial integrada\n"
                "Ventas · Compras · Inventario · Finanzas",
            )

            marca_texto.setObjectName(
                "LoginMarcaTexto",
            )

            marca_texto.setWordWrap(
                True,
            )

            fila_destacados = QHBoxLayout()

            fila_destacados.setSpacing(
                8,
            )

            for destacado in (
                "Multiempresa",
                "DIAN",
                "NIIF",
            ):

                etiqueta_destacado = QLabel(
                    destacado,
                )

                etiqueta_destacado.setObjectName(
                    "LoginDestacadoMarca",
                )

                fila_destacados.addWidget(
                    etiqueta_destacado,
                )

            fila_destacados.addStretch(
                1,
            )

            marca.addStretch(
                1,
            )

            marca.addWidget(
                marca_titulo,
            )

            marca.addWidget(
                marca_texto,
            )

            marca.addLayout(
                fila_destacados,
            )

            marca.addStretch(
                2,
            )

            panel_marca = QWidget()

            panel_marca.setObjectName(
                "LoginMarcaPanel",
            )

            panel_marca.setAutoFillBackground(
                False,
            )

            panel_marca.setFixedWidth(
                380,
            )

            panel_marca.setLayout(
                marca,
            )

        panel = QFrame()

        panel.setObjectName(
            "LoginPanel",
        )

        habilitar_fondo_qss(
            panel,
        )

        panel.setMinimumWidth(
            360,
        )

        panel.setFixedWidth(
            400,
        )

        panel.setMinimumHeight(
            400,
        )

        sombra = QGraphicsDropShadowEffect(
            panel,
        )

        sombra.setBlurRadius(
            42,
        )

        sombra.setOffset(
            0,
            12,
        )

        sombra.setColor(
            QColor(
                7,
                30,
                58,
                90,
            ),
        )

        panel.setGraphicsEffect(
            sombra,
        )

        panel.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Preferred,
        )

        layout_panel = QVBoxLayout(
            panel,
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

        cabecera = QFrame()

        cabecera.setObjectName(
            "LoginPanelCabecera",
        )

        habilitar_fondo_qss(
            cabecera,
        )

        cabecera_layout = QVBoxLayout(
            cabecera,
        )

        cabecera_layout.setContentsMargins(
            28,
            22,
            28,
            20,
        )

        cabecera_layout.setSpacing(
            4,
        )

        titulo = QLabel(
            "ERP NEXUS",
        )

        titulo.setObjectName(
            "LoginTitulo",
        )

        titulo.setAlignment(
            Qt.AlignCenter,
        )

        subtitulo = QLabel(
            "Inicio de sesión",
        )

        subtitulo.setObjectName(
            "LoginSubtitulo",
        )

        subtitulo.setAlignment(
            Qt.AlignCenter,
        )

        detalle_cabecera = QLabel(
            "Accede a ventas, compras, inventario y finanzas",
        )

        detalle_cabecera.setObjectName(
            "LoginCabeceraDetalle",
        )

        detalle_cabecera.setAlignment(
            Qt.AlignCenter,
        )

        if embebido:

            cabecera_layout.addWidget(
                subtitulo,
            )

            cabecera_layout.addWidget(
                detalle_cabecera,
            )

        else:

            cabecera_layout.addWidget(
                titulo,
            )

            cabecera_layout.addWidget(
                subtitulo,
            )

            cabecera_layout.addWidget(
                detalle_cabecera,
            )

        layout_panel.addWidget(
            cabecera,
        )

        cuerpo = QWidget()

        cuerpo.setObjectName(
            "LoginPanelCuerpo",
        )

        layout = QVBoxLayout(
            cuerpo,
        )

        layout.setContentsMargins(
            28,
            22,
            28,
            28,
        )

        layout.setSpacing(
            8,
        )

        fila_modulos = QHBoxLayout()

        fila_modulos.setSpacing(
            6,
        )

        for modulo in (
            "Ventas",
            "Compras",
            "Inventario",
            "Finanzas",
        ):

            chip = QLabel(
                modulo,
            )

            chip.setObjectName(
                "LoginModuloChip",
            )

            chip.setAlignment(
                Qt.AlignCenter,
            )

            fila_modulos.addWidget(
                chip,
            )

        layout.addLayout(
            fila_modulos,
        )

        layout.addSpacing(
            8,
        )

        etiqueta_usuario = QLabel(
            "Usuario",
        )

        etiqueta_usuario.setObjectName(
            "LoginEtiquetaCampo",
        )

        layout.addWidget(
            etiqueta_usuario,
        )

        self.txt_usuario = QLineEdit()

        self.txt_usuario.setObjectName(
            "LoginCampo",
        )

        self.txt_usuario.returnPressed.connect(
            lambda: self.txt_password.setFocus(),
        )

        layout.addWidget(
            self.txt_usuario,
        )

        etiqueta_password = QLabel(
            "Contraseña",
        )

        etiqueta_password.setObjectName(
            "LoginEtiquetaCampo",
        )

        layout.addWidget(
            etiqueta_password,
        )

        self.txt_password = QLineEdit()

        self.txt_password.setObjectName(
            "LoginCampo",
        )

        self.txt_password.setEchoMode(
            QLineEdit.Password,
        )

        self.txt_password.returnPressed.connect(
            self.iniciar_sesion,
        )

        layout.addWidget(
            self.txt_password,
        )

        layout.addSpacing(
            12,
        )

        self.btn_login = QPushButton(
            "Iniciar sesión",
        )

        self.btn_login.setObjectName(
            "LoginBoton",
        )

        self.btn_login.clicked.connect(
            self.iniciar_sesion,
        )

        layout.addWidget(
            self.btn_login,
        )

        layout_panel.addWidget(
            cuerpo,
        )

        if embebido:

            fila_central.addStretch(
                1,
            )

            fila_central.addWidget(
                panel_marca,
                0,
                Qt.AlignmentFlag.AlignVCenter,
            )

            fila_central.addWidget(
                panel,
                0,
                Qt.AlignmentFlag.AlignVCenter,
            )

            fila_central.addStretch(
                1,
            )

            layout_raiz.addStretch(
                1,
            )

            layout_raiz.addLayout(
                fila_central,
            )

            layout_raiz.addStretch(
                1,
            )

        else:

            layout_raiz.addStretch()

            layout_raiz.addWidget(
                panel,
                0,
                Qt.AlignmentFlag.AlignHCenter,
            )

            layout_raiz.addStretch()

        self.txt_usuario.setFocus()

    def paintEvent(
        self,
        event,
    ) -> None:

        painter = QPainter(
            self,
        )

        try:

            pintar_fondo_login(
                painter,
                self.rect(),
            )

        finally:

            painter.end()

        super().paintEvent(
            event,
        )

    def reiniciar(
        self,
    ) -> None:

        self._restablecer_boton()

        self.txt_password.clear()

        self.txt_usuario.setFocus()

    def _restablecer_boton(self):

        self._timer.stop()
        self._conectando = False
        self.btn_login.setEnabled(True)
        self.btn_login.setText("Iniciar sesión")

    def _tiempo_agotado(self):

        if not self._conectando:

            return

        self._restablecer_boton()

        if self._hilo is not None and self._hilo.isRunning():

            self._hilo.requestInterruption()
            self._hilo.quit()
            self._hilo.wait(2000)

        QMessageBox.critical(
            self,
            "Error de conexión",
            (
                "La conexión tardó demasiado.\n\n"
                "Verifique que PostgreSQL esté activo y "
                "cierre otras ventanas del ERP que puedan "
                "estar abiertas."
            ),
        )

    def iniciar_sesion(self):

        if self._conectando:

            return

        usuario = self.txt_usuario.text().strip()
        password = self.txt_password.text()

        if not usuario:

            QMessageBox.warning(
                self,
                "Error",
                "Ingrese el usuario.",
            )
            self.txt_usuario.setFocus()
            return

        self._conectando = True
        self.btn_login.setEnabled(False)
        self.btn_login.setText("Conectando...")

        self._hilo = QThread()
        self._trabajo = TrabajoInicioSesion(
            usuario,
            password,
        )
        self._trabajo.moveToThread(self._hilo)

        self._hilo.started.connect(self._trabajo.ejecutar)
        self._trabajo.terminado.connect(self._sesion_terminada)
        self._trabajo.terminado.connect(self._hilo.quit)
        self._hilo.finished.connect(self._hilo.deleteLater)

        self._hilo.start()
        self._timer.start(self._TIMEOUT_MS)

    def _sesion_terminada(
        self,
        resultado,
        error,
    ):

        if not self._conectando:

            return

        self._restablecer_boton()

        usuario = self.txt_usuario.text().strip()

        if error:

            QMessageBox.critical(
                self,
                "Error de conexión",
                (
                    "No se pudo conectar con la "
                    "base de datos.\n\n"
                    f"{error}\n\n"
                    "Verifique que PostgreSQL "
                    "esté activo y el archivo "
                    ".env sea correcto."
                ),
            )
            return

        if isinstance(
            resultado,
            dict,
        ) and "error_login" in resultado:

            from aplicacion.nucleo.auditoria import Auditoria

            Auditoria.registrar(
                usuario,
                "login_denegado",
                str(
                    resultado["error_login"],
                ),
                modulo="Seguridad",
                exito=False,
            )

            QMessageBox.warning(
                self,
                "Acceso denegado",
                resultado["error_login"],
            )

            self.txt_password.clear()
            self.txt_usuario.setFocus()
            return

        if isinstance(
            resultado,
            dict,
        ) and "licencia" in resultado:

            estado = resultado["licencia"]

            dialogo = DialogoActivacionLicencia(
                mensaje=estado.mensaje,
                parent=self,
            )

            if (
                dialogo.exec()
                and dialogo.activada
            ):

                self.iniciar_sesion()

            return

        if resultado:

            if self._embebido:

                self.sesion_iniciada.emit(
                    resultado,
                )

                return

            from aplicacion.interfaz.dashboard import (
                Dashboard,
            )

            self.dashboard = Dashboard(
                resultado,
            )

            self.dashboard.show()

            self.close()

            self.deleteLater()

            return

        from aplicacion.nucleo.auditoria import Auditoria

        Auditoria.registrar(
            usuario,
            "login_fallido",
            "Credenciales incorrectas.",
            modulo="Seguridad",
            exito=False,
        )

        QMessageBox.warning(
            self,
            "Error",
            "Usuario o contraseña incorrectos.",
        )
        self.txt_password.clear()
        self.txt_usuario.setFocus()
