from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PortalAccesoWidget(QWidget):
    """
    Genera y muestra el enlace de autoconsulta del portal web
    (ver facturas y estado de cartera) para un Cliente/Proveedor.
    """

    def __init__(
        self,
        tercero_id: int,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.tercero_id = tercero_id

        layout = QVBoxLayout(
            self,
        )

        layout.addWidget(
            QLabel(
                "El cliente o proveedor usa este enlace para "
                "consultar sus facturas y estado de cartera "
                "sin necesidad de una cuenta del ERP.",
            ),
        )

        self.txt_enlace = QLineEdit()

        self.txt_enlace.setReadOnly(
            True,
        )

        self.txt_enlace.setPlaceholderText(
            "Sin acceso generado",
        )

        layout.addWidget(
            self.txt_enlace,
        )

        botones = QHBoxLayout()

        self.btn_generar = QPushButton(
            "Generar / regenerar acceso",
        )

        self.btn_generar.clicked.connect(
            self._generar,
        )

        self.btn_copiar = QPushButton(
            "Copiar enlace",
        )

        self.btn_copiar.clicked.connect(
            self._copiar,
        )

        botones.addWidget(
            self.btn_generar,
        )

        botones.addWidget(
            self.btn_copiar,
        )

        botones.addStretch()

        layout.addLayout(
            botones,
        )

        layout.addStretch()

        self._cargar()

    def _url(
        self,
        token: str,
    ) -> str:

        from aplicacion.nucleo.configuracion import (
            Configuracion,
        )

        puerto = (
            Configuracion.obtener(
                "api",
                "puerto",
            )
            or 8765
        )

        return (
            f"http://127.0.0.1:{puerto}"
            f"/portal/mi-cuenta/{token}"
        )

    def _cargar(
        self,
    ) -> None:

        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )

        tercero = TerceroServicio.obtener_por_id(
            self.tercero_id,
        )

        token = getattr(
            tercero,
            "portal_token",
            None,
        )

        self.txt_enlace.setText(
            self._url(
                token,
            )
            if token
            else "",
        )

    def _generar(
        self,
    ) -> None:

        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )

        token = TerceroServicio.generar_token_portal(
            self.tercero_id,
        )

        if token is None:

            QMessageBox.warning(
                self,
                "Portal",
                "No se pudo generar el acceso.",
            )

            return

        self.txt_enlace.setText(
            self._url(
                token,
            ),
        )

    def _copiar(
        self,
    ) -> None:

        if not self.txt_enlace.text():

            QMessageBox.information(
                self,
                "Portal",
                "Genere el acceso antes de copiarlo.",
            )

            return

        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(
            self.txt_enlace.text(),
        )
