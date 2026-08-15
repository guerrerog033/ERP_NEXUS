from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from aplicacion.maestros.empresas.servicios import (
    EmpresaServicio,
)


class LogoEmpresaWidget(QWidget):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self._archivo_local: str | None = None
        self._ruta_relativa: str | None = None

        self._crear_ui()

    def _crear_ui(self):

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.preview = QLabel(
            "Sin logo",
        )

        self.preview.setAlignment(
            Qt.AlignCenter,
        )

        self.preview.setFixedSize(
            220,
            110,
        )

        self.preview.setStyleSheet(
            """
            QLabel {
                border: 1px solid #cfd8dc;
                border-radius: 8px;
                background: #fafafa;
                color: #78909c;
            }
            """
        )

        botones = QHBoxLayout()

        self.btn_seleccionar = QPushButton(
            "Seleccionar logo",
        )

        self.btn_quitar = QPushButton(
            "Quitar",
        )

        botones.addWidget(
            self.btn_seleccionar,
        )

        botones.addWidget(
            self.btn_quitar,
        )

        botones.addStretch()

        layout.addWidget(
            self.preview,
            alignment=Qt.AlignLeft,
        )

        layout.addLayout(
            botones,
        )

        self.btn_seleccionar.clicked.connect(
            self._seleccionar,
        )

        self.btn_quitar.clicked.connect(
            self._quitar,
        )

    def _seleccionar(self):

        archivo, _ = QFileDialog.getOpenFileName(

            self,

            "Seleccionar logo",

            "",

            "Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)",

        )

        if not archivo:

            return

        self.establecer_archivo(
            archivo,
        )

    def _quitar(self):

        self._archivo_local = None
        self._ruta_relativa = None

        self.preview.setText(
            "Sin logo",
        )

        self.preview.setPixmap(
            QPixmap(),
        )

    def establecer_archivo(
        self,
        archivo: str,
    ):

        ruta = Path(
            archivo,
        )

        if not ruta.is_file():

            return

        pixmap = QPixmap(
            str(ruta),
        )

        if pixmap.isNull():

            return

        self._archivo_local = str(
            ruta,
        )

        self._ruta_relativa = None

        self._mostrar_pixmap(
            pixmap,
        )

    def establecer_ruta_relativa(
        self,
        ruta_relativa: str | None,
    ):

        self._ruta_relativa = ruta_relativa
        self._archivo_local = None

        ruta = EmpresaServicio.ruta_logo_absoluta(
            ruta_relativa,
        )

        if ruta is None:

            self._quitar()

            return

        pixmap = QPixmap(
            str(ruta),
        )

        self._mostrar_pixmap(
            pixmap,
        )

    def _mostrar_pixmap(
        self,
        pixmap: QPixmap,
    ):

        escala = pixmap.scaled(

            self.preview.size(),

            Qt.KeepAspectRatio,

            Qt.SmoothTransformation,

        )

        self.preview.setPixmap(
            escala,
        )

        self.preview.setText(
            "",
        )

    def archivo_pendiente(self) -> str | None:

        return self._archivo_local

    def ruta_relativa(self) -> str | None:

        return self._ruta_relativa
