from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from aplicacion.interfaz.dashboard import Dashboard
from aplicacion.interfaz.login import Login


class VentanaPrincipal(QMainWindow):

    INDICE_LOGIN = 0
    INDICE_DASHBOARD = 1

    def __init__(
        self,
    ):

        super().__init__()

        self.setWindowTitle(
            "ERP NEXUS",
        )

        self.resize(
            1280,
            800,
        )

        self.setStyleSheet(
            "QMainWindow { background-color: #071E3A; }",
        )

        self._dashboard: Dashboard | None = None

        self._stack = QStackedWidget()

        self._stack.setObjectName(
            "StackPrincipal",
        )

        self.setCentralWidget(
            self._stack,
        )

        self._login = Login(
            embebido=True,
        )

        self._login.sesion_iniciada.connect(
            self._mostrar_dashboard,
        )

        self._stack.addWidget(
            self._login,
        )

        self._stack.setCurrentIndex(
            self.INDICE_LOGIN,
        )

        self.showMaximized()

    def _mostrar_dashboard(
        self,
        usuario,
    ) -> None:

        self._liberar_dashboard()

        self._dashboard = Dashboard(
            usuario,
            embebido=True,
        )

        self._dashboard.cerrar_sesion_solicitado.connect(
            self._mostrar_login,
        )

        self._stack.addWidget(
            self._dashboard,
        )

        self._stack.setCurrentWidget(
            self._dashboard,
        )

        self.setWindowTitle(
            self._dashboard._titulo_ventana(),
        )

    def _mostrar_login(
        self,
    ) -> None:

        self._liberar_dashboard()

        self._login.reiniciar()

        self._stack.setCurrentIndex(
            self.INDICE_LOGIN,
        )

        self.setWindowTitle(
            "ERP NEXUS",
        )

    def _liberar_dashboard(
        self,
    ) -> None:

        if self._dashboard is None:

            return

        self._dashboard.preparar_cierre()

        indice = self._stack.indexOf(
            self._dashboard,
        )

        if indice >= 0:

            widget = self._stack.widget(
                indice,
            )

            self._stack.removeWidget(
                widget,
            )

            widget.deleteLater()

        self._dashboard = None
