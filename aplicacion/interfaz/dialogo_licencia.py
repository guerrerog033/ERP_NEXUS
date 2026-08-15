from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from aplicacion.licencias.servicios import (
    activar_serial,
)
from aplicacion.nucleo.configuracion import Configuracion


class DialogoActivacionLicencia(QDialog):

    def __init__(
        self,
        mensaje: str = "",
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self._activada = False

        self.setWindowTitle(
            "Activar licencia - ERP NEXUS",
        )

        self.setModal(
            True,
        )

        self.resize(
            460,
            320,
        )

        layout = QVBoxLayout(
            self,
        )

        titulo = QLabel(
            "Activación de licencia",
        )

        titulo.setAlignment(
            Qt.AlignCenter,
        )

        titulo.setStyleSheet(
            """
            font-size:18px;
            font-weight:bold;
            color:#1B4F8A;
            padding-bottom:8px;
            """
        )

        layout.addWidget(
            titulo,
        )

        texto = (
            mensaje
            or (
                "Ingrese el serial de licencia "
                "proporcionado por su proveedor."
            )
        )

        self.lbl_mensaje = QLabel(
            texto,
        )

        self.lbl_mensaje.setWordWrap(
            True,
        )

        layout.addWidget(
            self.lbl_mensaje,
        )

        formulario = QFormLayout()

        self.txt_serial = QLineEdit()

        self.txt_serial.setPlaceholderText(
            "NEXUS-XXXX-XXXX-XXXX-XXXX-XXXX",
        )

        formulario.addRow(
            "Serial",
            self.txt_serial,
        )

        self.txt_titular = QLineEdit()

        self.txt_titular.setPlaceholderText(
            "Razón social o nombre",
        )

        formulario.addRow(
            "Titular",
            self.txt_titular,
        )

        self.txt_nit = QLineEdit()

        self.txt_nit.setPlaceholderText(
            "NIT (opcional)",
        )

        formulario.addRow(
            "NIT",
            self.txt_nit,
        )

        layout.addLayout(
            formulario,
        )

        empresa = (
            Configuracion.obtener(
                "erp",
                "empresa_desarrolladora",
            )
            or "NEXUS SOFTWARE"
        )

        ayuda = QLabel(
            f"Para adquirir una licencia contacte a "
            f"{empresa}."
        )

        ayuda.setWordWrap(
            True,
        )

        ayuda.setStyleSheet(
            "color:#555;font-size:11px;",
        )

        layout.addWidget(
            ayuda,
        )

        botones = QHBoxLayout()

        self.btn_activar = QPushButton(
            "Activar",
        )

        self.btn_activar.clicked.connect(
            self._activar,
        )

        btn_cancelar = QPushButton(
            "Salir",
        )

        btn_cancelar.clicked.connect(
            self.reject,
        )

        botones.addStretch()

        botones.addWidget(
            self.btn_activar,
        )

        botones.addWidget(
            btn_cancelar,
        )

        layout.addLayout(
            botones,
        )

        self.txt_serial.setFocus()

        self.txt_serial.returnPressed.connect(
            self._activar,
        )

    @property
    def activada(
        self,
    ) -> bool:

        return self._activada

    def _activar(
        self,
    ) -> None:

        serial = self.txt_serial.text().strip()

        if not serial:

            QMessageBox.warning(
                self,
                "Serial requerido",
                "Ingrese el serial de licencia.",
            )

            self.txt_serial.setFocus()

            return

        self.btn_activar.setEnabled(
            False,
        )

        try:

            estado = activar_serial(
                serial,
                titular=(
                    self.txt_titular.text().strip()
                ),
                nit_cliente=(
                    self.txt_nit.text().strip()
                ),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                str(
                    error,
                ),
            )

            self.btn_activar.setEnabled(
                True,
            )

            return

        if not estado.valida:

            QMessageBox.warning(
                self,
                "Activación fallida",
                estado.mensaje
                or "No se pudo activar la licencia.",
            )

            self.btn_activar.setEnabled(
                True,
            )

            return

        self._activada = True

        mensaje = (
            f"Licencia {estado.edicion_nombre} "
            f"activada correctamente."
        )

        if estado.fecha_vencimiento:

            mensaje += (
                "\n\nVence: "
                f"{estado.fecha_vencimiento.strftime('%d/%m/%Y')}"
            )

        QMessageBox.information(
            self,
            "Licencia activada",
            mensaje,
        )

        self.accept()
