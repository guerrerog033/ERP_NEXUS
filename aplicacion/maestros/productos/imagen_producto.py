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

from aplicacion.maestros.productos.servicios import (
    ServicioProducto,
)


class ImagenProductoWidget(QWidget):

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
            "Sin imagen",
        )

        self.preview.setAlignment(
            Qt.AlignCenter,
        )

        self.preview.setFixedSize(
            160,
            160,
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
            "Seleccionar imagen",
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

            "Seleccionar imagen",

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
            "Sin imagen",
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

        ruta = ServicioProducto.ruta_imagen_absoluta(
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


class ImagenProductoLabel(
    QLabel,
):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self._pixmap: QPixmap | None = None

        self.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )

        self.setFixedSize(
            56,
            56,
        )

        self.setStyleSheet(
            "background: #F8FAFC; "
            "border: 1px dashed #C8D8E8; "
            "border-radius: 4px;",
        )

    def establecer_producto(
        self,
        producto,
    ) -> None:

        pixmap = ServicioProducto.cargar_pixmap_producto(
            producto,
        )

        if pixmap is not None:

            self.establecer_pixmap(
                pixmap,
            )

            return

        ruta = ServicioProducto.resolver_imagen_producto(
            producto,
        )

        self.establecer_ruta(
            ruta,
        )

    def establecer_ruta_relativa(
        self,
        ruta_relativa: str | None,
        codigo: str | None = None,
    ) -> None:

        ruta = ServicioProducto.ruta_imagen_absoluta(
            ruta_relativa,
        )

        if (
            ruta is None
            and codigo
        ):

            ruta = ServicioProducto.ruta_imagen_por_codigo(
                codigo,
            )

        self.establecer_ruta(
            ruta,
        )

    def establecer_ruta(
        self,
        ruta: Path | None,
    ) -> None:

        if (
            ruta is None
            or not ruta.is_file()
        ):

            self._pixmap = None

            self.clear()

            return

        self._pixmap = QPixmap(
            str(ruta),
        )

        self.establecer_pixmap(
            self._pixmap,
        )

    def establecer_pixmap(
        self,
        pixmap: QPixmap | None,
    ) -> None:

        if (
            pixmap is None
            or pixmap.isNull()
        ):

            self._pixmap = None

            self.setScaledContents(
                False,
            )

            self.clear()

            return

        self._pixmap = pixmap

        self.setScaledContents(
            True,
        )

        self.setPixmap(
            pixmap,
        )

    def _actualizar_pixmap(
        self,
    ) -> None:

        if (
            self._pixmap is None
            or self._pixmap.isNull()
        ):

            self.setScaledContents(
                False,
            )

            self.clear()

            return

        self.setScaledContents(
            True,
        )

        self.setPixmap(
            self._pixmap,
        )

    def resizeEvent(
        self,
        event,
    ):

        super().resizeEvent(
            event,
        )

        self._actualizar_pixmap()

    def showEvent(
        self,
        event,
    ):

        super().showEvent(
            event,
        )

        self._actualizar_pixmap()
