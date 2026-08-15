from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
)

from aplicacion.recursos.estilos.tema import habilitar_fondo_qss
from aplicacion.recursos.ui.recursos import Recursos


class BotonModulo(QFrame):

    clicked = Signal()

    ANCHO_ICONO = 24

    def __init__(
        self,
        icono: str,
        titulo: str,
        modulo: str,
        *,
        pendiente: bool = False,
    ):

        super().__init__()

        self.modulo = modulo
        self._pendiente = pendiente

        self.setObjectName(
            "BotonModuloPendiente"
            if pendiente
            else "BotonModulo",
        )

        habilitar_fondo_qss(
            self,
        )

        self.setCursor(
            Qt.ForbiddenCursor
            if pendiente
            else Qt.PointingHandCursor,
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        self.setMinimumHeight(
            44,
        )

        self._layout = QHBoxLayout(
            self,
        )

        self._layout.setContentsMargins(
            16,
            8,
            12,
            8,
        )

        self._layout.setSpacing(
            12,
        )

        self.lbl_icono = QLabel()

        self.lbl_icono.setObjectName(
            "BotonModuloIcono",
        )

        self.lbl_icono.setAlignment(
            Qt.AlignCenter,
        )

        self.lbl_icono.setFixedSize(
            self.ANCHO_ICONO,
            self.ANCHO_ICONO,
        )

        self.lbl_icono.setPixmap(
            Recursos.icono_modulo(
                icono,
            ).pixmap(
                self.ANCHO_ICONO,
                self.ANCHO_ICONO,
            ),
        )

        self.lbl_titulo = QLabel(
            titulo
            + (
                "  ·  Próx."
                if pendiente
                else ""
            ),
        )

        self._titulo_base = titulo

        self.lbl_titulo.setObjectName(
            "BotonModuloTitulo",
        )

        self.lbl_titulo.setAlignment(
            Qt.AlignVCenter
            | Qt.AlignLeft,
        )

        self.lbl_titulo.setFont(
            QFont(
                "Segoe UI",
                10,
            ),
        )

        self._layout.addWidget(
            self.lbl_icono,
            0,
            Qt.AlignVCenter,
        )

        self._layout.addWidget(
            self.lbl_titulo,
            1,
        )

        if pendiente:

            self.setToolTip(
                "Módulo disponible próximamente",
            )

    def mousePressEvent(
        self,
        event,
    ):

        if event.button() == Qt.LeftButton:

            if not self._pendiente:

                self.clicked.emit()

        super().mousePressEvent(
            event,
        )

    def set_submenu_abierto(
        self,
        abierto: bool,
    ) -> None:

        nombre = (
            "BotonModuloActivo"
            if abierto
            and not self._pendiente
            else (
                "BotonModuloPendiente"
                if self._pendiente
                else "BotonModulo"
            )
        )

        self.setObjectName(
            nombre,
        )

        self.style().unpolish(
            self,
        )

        self.style().polish(
            self,
        )

    def set_expandido(
        self,
        expandido: bool,
    ) -> None:

        self.lbl_titulo.setVisible(
            expandido,
        )

        if expandido:

            self._layout.setContentsMargins(
                16,
                8,
                12,
                8,
            )

            if self._pendiente:

                self.setToolTip(
                    "Módulo disponible próximamente",
                )

            else:

                self.setToolTip(
                    "",
                )

            return

        self._layout.setContentsMargins(
            10,
            8,
            10,
            8,
        )

        self.setToolTip(
            self._titulo_base,
        )

    def configurar_ancho_colapsado(
        self,
        ancho: int,
    ) -> None:

        self.lbl_icono.setFixedSize(
            min(
                ancho - 20,
                self.ANCHO_ICONO,
            ),
            self.ANCHO_ICONO,
        )


class BotonSubmodulo(QFrame):

    clicked = Signal()
    favorito_solicitado = Signal(str)

    def __init__(
        self,
        titulo: str,
        modulo: str,
        *,
        margen_izquierdo: int = 52,
    ):

        super().__init__()

        self.modulo = modulo

        self.setObjectName(
            "BotonSubmodulo",
        )

        habilitar_fondo_qss(
            self,
        )

        self.setCursor(
            Qt.PointingHandCursor,
        )

        self.setFixedHeight(
            36,
        )

        layout = QHBoxLayout(
            self,
        )

        layout.setContentsMargins(
            margen_izquierdo,
            4,
            12,
            4,
        )

        etiqueta = QLabel(
            titulo,
        )

        etiqueta.setObjectName(
            "BotonSubmoduloTitulo",
        )

        etiqueta.setFont(
            QFont(
                "Segoe UI",
                10,
            ),
        )

        layout.addWidget(
            etiqueta,
        )

        self.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu,
        )

        self.customContextMenuRequested.connect(
            self._mostrar_menu_contexto,
        )

    def _mostrar_menu_contexto(
        self,
        pos,
    ) -> None:

        from PySide6.QtWidgets import QMenu

        from aplicacion.framework.app_context import AppContext

        menu = QMenu(
            self,
        )

        navegacion = getattr(
            AppContext,
            "navegacion",
            None,
        )

        if navegacion and navegacion.es_favorito(
            self.modulo,
        ):

            menu.addAction(
                "Quitar de favoritos",
                lambda: self._alternar_favorito(),
            )

        else:

            menu.addAction(
                "Agregar a favoritos",
                lambda: self._alternar_favorito(),
            )

        menu.exec(
            self.mapToGlobal(
                pos,
            ),
        )

    def _alternar_favorito(
        self,
    ) -> None:

        from aplicacion.framework.app_context import AppContext

        navegacion = getattr(
            AppContext,
            "navegacion",
            None,
        )

        if navegacion is None:

            self.favorito_solicitado.emit(
                self.modulo,
            )

            return

        navegacion.alternar_favorito(
            self.modulo,
        )

        self.favorito_solicitado.emit(
            self.modulo,
        )

    def mousePressEvent(
        self,
        event,
    ):

        if event.button() == Qt.LeftButton:

            self.clicked.emit()

        super().mousePressEvent(
            event,
        )
