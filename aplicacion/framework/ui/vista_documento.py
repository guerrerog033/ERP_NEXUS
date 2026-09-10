from __future__ import annotations

from abc import abstractmethod
from pathlib import Path

from PySide6.QtCore import QEvent, Qt, QUrl, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
)

from aplicacion.framework.base.page import Page
from aplicacion.recursos.ui.botones import Botones


class VistaDocumento(Page):

    editar_solicitado = Signal()
    actualizado = Signal()
    cerrar = Signal()

    ancho = 1120
    alto = 780

    definition = None

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.id_registro = id_registro

        super().__init__(
            parent=parent,
        )

        self._cargar_datos()

    def _crear_ui(self):

        super()._crear_ui()

        self.layout_principal.setContentsMargins(
            12,
            10,
            12,
            10,
        )

        self.layout_principal.setSpacing(
            10,
        )

        encabezado = QHBoxLayout()

        encabezado.setSpacing(
            10,
        )

        self.lbl_titulo = QLabel()

        self.lbl_titulo.setObjectName(
            "DocumentoTitulo",
        )

        self.lbl_estado = QLabel()

        self.lbl_estado.setObjectName(
            "DocumentoBadge",
        )

        self.lbl_estado.setVisible(
            False,
        )

        self.lbl_formato = QLabel()

        self.lbl_formato.setObjectName(
            "DocumentoFormatoChip",
        )

        encabezado.addWidget(
            self.lbl_titulo,
        )

        encabezado.addWidget(
            self.lbl_estado,
        )

        encabezado.addStretch()

        encabezado.addWidget(
            self.lbl_formato,
        )

        self.layout_principal.addLayout(
            encabezado,
        )

        self._agregar_barras_accion()

        marco = QFrame()

        marco.setObjectName(
            "DocumentoPreviewMarco",
        )

        marco_layout = QVBoxLayout(
            marco,
        )

        marco_layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        self.vista_html = QTextBrowser()

        self.vista_html.setObjectName(
            "DocumentoPreviewHtml",
        )

        self.vista_html.setOpenExternalLinks(
            True,
        )

        self.vista_html.setFrameShape(
            QFrame.Shape.NoFrame,
        )

        self.vista_html.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        raiz = Path(
            __file__,
        ).resolve().parents[
            2
        ]

        self.vista_html.document().setBaseUrl(
            QUrl.fromLocalFile(
                str(
                    raiz,
                )
                + "/",
            ),
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True,
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame,
        )

        scroll.setWidget(
            self.vista_html,
        )

        self._scroll_preview = scroll

        marco_layout.addWidget(
            scroll,
        )

        self.layout_principal.addWidget(
            marco,
            1,
        )

        self._conectar_acciones()

        self._activar_atajos_documento()

        self._scroll_preview.viewport().installEventFilter(
            self,
        )

    def _activar_atajos_documento(
        self,
    ) -> None:

        atajos = (
            ("Ctrl+P", self._imprimir),
            ("Ctrl+Shift+P", self._exportar_pdf),
            ("Ctrl+E", self._editar_por_atajo),
        )

        for secuencia, accion in atajos:

            QShortcut(
                QKeySequence(secuencia),
                self,
                activated=accion,
            )

    def _editar_por_atajo(
        self,
    ) -> None:

        boton = getattr(
            self,
            "btn_editar",
            None,
        )

        if boton is not None and boton.isEnabled() and boton.isVisible():

            self.editar_solicitado.emit()

    def establecer_estado(
        self,
        texto: str,
        tono: str = "neutral",
    ) -> None:
        """
        Fija el badge de estado de la cabecera. ``tono`` admite
        ``neutral``, ``info``, ``exito``, ``advertencia`` y
        ``peligro`` (definidos en tema.qss).
        """

        self.lbl_estado.setText(
            texto or "",
        )

        self.lbl_estado.setVisible(
            bool(texto),
        )

        if self.lbl_estado.property("tono") != tono:

            self.lbl_estado.setProperty(
                "tono",
                tono,
            )

            self.lbl_estado.style().unpolish(
                self.lbl_estado,
            )

            self.lbl_estado.style().polish(
                self.lbl_estado,
            )

    def _agregar_barras_accion(
        self,
    ) -> None:

        self.btn_editar = Botones.editar()

        self.btn_imprimir = Botones.editar()

        self.btn_imprimir.setText(
            "Imprimir",
        )

        self.btn_pdf = Botones.aceptar()

        self.btn_pdf.setText(
            "PDF",
        )

        self.btn_cerrar = Botones.cerrar()

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                self.etiqueta_barra_principal(),
                (
                    self.btn_editar,
                    self.btn_imprimir,
                    self.btn_pdf,
                    self.btn_cerrar,
                ),
                separar_ultimo=True,
            ),
        )

    def _conectar_acciones(
        self,
    ) -> None:

        self.btn_editar.clicked.connect(
            self.editar_solicitado.emit,
        )

        self.btn_imprimir.clicked.connect(
            self._imprimir,
        )

        self.btn_pdf.clicked.connect(
            self._exportar_pdf,
        )

        self.btn_cerrar.clicked.connect(
            self.cerrar.emit,
        )

    def etiqueta_barra_principal(
        self,
    ) -> str:

        return "Documento"

    @abstractmethod
    def _cargar_datos(
        self,
    ) -> None:

        raise NotImplementedError

    @abstractmethod
    def _imprimir(
        self,
    ) -> None:

        raise NotImplementedError

    @abstractmethod
    def _exportar_pdf(
        self,
    ) -> None:

        raise NotImplementedError

    def recargar(
        self,
    ) -> None:

        self._cargar_datos()

        self.actualizado.emit()

    def mostrar_formato(
        self,
        texto: str,
    ) -> None:

        self.lbl_formato.setText(
            texto,
        )

        self.lbl_formato.setVisible(
            bool(
                texto,
            ),
        )

    def establecer_html(
        self,
        html: str,
    ) -> None:

        self.vista_html.setHtml(
            html,
        )

        self._ajustar_vista_previa()

    def eventFilter(
        self,
        watched,
        event,
    ):

        if (
            hasattr(
                self,
                "_scroll_preview",
            )
            and watched
            is self._scroll_preview.viewport()
            and event.type()
            == QEvent.Type.Resize
        ):

            self._ajustar_vista_previa()

        return super().eventFilter(
            watched,
            event,
        )

    def showEvent(
        self,
        event,
    ):

        super().showEvent(
            event,
        )

        self._ajustar_vista_previa()

    def resizeEvent(
        self,
        event,
    ):

        super().resizeEvent(
            event,
        )

        self._ajustar_vista_previa()

    def _ajustar_vista_previa(
        self,
    ) -> None:

        if not hasattr(
            self,
            "vista_html",
        ):

            return

        if not hasattr(
            self,
            "_scroll_preview",
        ):

            return

        ancho = (
            self._scroll_preview.viewport().width()
            - 16
        )

        if ancho < 200:

            return

        self.vista_html.document().setTextWidth(
            float(
                ancho,
            ),
        )

    @staticmethod
    def _barra_etiquetada(
        titulo: str,
        botones: tuple[
            QPushButton,
            ...,
        ],
        *,
        separar_ultimo: bool = False,
    ) -> QHBoxLayout:

        contenedor = QHBoxLayout()

        contenedor.setSpacing(
            12,
        )

        etiqueta = QLabel(
            titulo,
        )

        etiqueta.setObjectName(
            "BarraAccionEtiqueta",
        )

        etiqueta.setMinimumWidth(
            88,
        )

        contenedor.addWidget(
            etiqueta,
        )

        fila = QHBoxLayout()

        fila.setSpacing(
            8,
        )

        for boton in botones:

            if (
                separar_ultimo
                and boton is botones[
                    -1
                ]
            ):

                fila.addStretch()

            fila.addWidget(
                boton,
            )

        if not separar_ultimo:

            fila.addStretch()

        contenedor.addLayout(
            fila,
            1,
        )

        return contenedor

    @staticmethod
    def boton_accion(
        texto: str,
    ) -> QPushButton:

        boton = QPushButton(
            texto,
        )

        boton.setCursor(
            Qt.CursorShape.PointingHandCursor,
        )

        boton.setMinimumHeight(
            34,
        )

        return boton


def mostrar_dialogo_vista(
    vista_cls,
    id_registro: int,
    *,
    titulo: str,
    parent,
    ancho: int = 1120,
    alto: int = 780,
    al_editar=None,
    al_actualizar=None,
) -> None:

    from PySide6.QtWidgets import (
        QDialog,
        QVBoxLayout,
    )

    ventana = QDialog(
        parent,
    )

    ventana.setWindowTitle(
        titulo,
    )

    ventana.setModal(
        True,
    )

    vista = vista_cls(
        id_registro=id_registro,
        parent=ventana,
    )

    ventana.resize(
        min(
            vista.ancho,
            ancho,
        ),
        min(
            vista.alto,
            alto,
        ),
    )

    layout = QVBoxLayout(
        ventana,
    )

    layout.setContentsMargins(
        6,
        6,
        6,
        6,
    )

    layout.addWidget(
        vista,
    )

    if al_editar is not None:

        vista.editar_solicitado.connect(
            al_editar,
        )

    if al_actualizar is not None:

        vista.actualizado.connect(
            al_actualizar,
        )

    vista.cerrar.connect(
        ventana.accept,
    )

    ventana.exec()

    vista.deleteLater()
