from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
)

from aplicacion.recursos.estilos.tema import habilitar_fondo_qss
from aplicacion.recursos.ui.recursos import Recursos


COLOR_ICONO = "#B4C0CF"
COLOR_ICONO_ACTIVO = "#FFFFFF"


def _pixmap_tenido(
    icono,
    tamano: int,
    color: str,
) -> QPixmap:
    """
    Pinta el ícono SVG (de un solo trazo) con un color de la paleta,
    para que todos los íconos del menú se vean iguales y el activo
    tome el azul marino.
    """

    base = icono.pixmap(
        tamano,
        tamano,
    )

    resultado = QPixmap(
        base.size(),
    )

    resultado.setDevicePixelRatio(
        base.devicePixelRatio(),
    )

    resultado.fill(
        Qt.transparent,
    )

    pintor = QPainter(
        resultado,
    )

    pintor.drawPixmap(
        0,
        0,
        base,
    )

    pintor.setCompositionMode(
        QPainter.CompositionMode_SourceIn,
    )

    pintor.fillRect(
        resultado.rect(),
        QColor(
            color,
        ),
    )

    pintor.end()

    return resultado


class BotonModulo(QFrame):

    clicked = Signal()

    ANCHO_ICONO = 20

    def __init__(
        self,
        icono: str,
        titulo: str,
        modulo: str,
        *,
        pendiente: bool = False,
        con_submenu: bool = False,
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
            38,
        )

        self._layout = QHBoxLayout(
            self,
        )

        self._layout.setContentsMargins(
            12,
            6,
            10,
            6,
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

        icono_qt = Recursos.icono_modulo(
            icono,
        )

        self._pixmap_normal = _pixmap_tenido(
            icono_qt,
            self.ANCHO_ICONO,
            COLOR_ICONO,
        )

        self._pixmap_activo = _pixmap_tenido(
            icono_qt,
            self.ANCHO_ICONO,
            COLOR_ICONO_ACTIVO,
        )

        self.lbl_icono.setPixmap(
            self._pixmap_normal,
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

        # Flecha que indica que el módulo despliega opciones.
        self.lbl_flecha = QLabel(
            "›" if con_submenu else "",
        )

        self.lbl_flecha.setObjectName(
            "BotonModuloFlecha",
        )

        self.lbl_flecha.setFixedWidth(
            12,
        )

        if not con_submenu:

            self.lbl_flecha.setVisible(
                False,
            )

        self._con_submenu = con_submenu

        self._layout.addWidget(
            self.lbl_flecha,
            0,
            Qt.AlignVCenter,
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

        activo = nombre == "BotonModuloActivo"

        self.lbl_icono.setPixmap(
            self._pixmap_activo
            if activo
            else self._pixmap_normal,
        )

        if self._con_submenu:

            self.lbl_flecha.setText(
                "⌄" if abierto else "›",
            )

        self._repulir()

    def _repulir(
        self,
    ) -> None:

        for widget in (
            self,
            self.lbl_titulo,
            self.lbl_flecha,
        ):

            widget.style().unpolish(
                widget,
            )

            widget.style().polish(
                widget,
            )

    def set_expandido(
        self,
        expandido: bool,
    ) -> None:

        self.lbl_titulo.setVisible(
            expandido,
        )

        self.lbl_flecha.setVisible(
            expandido
            and self._con_submenu,
        )

        if expandido:

            self._layout.setContentsMargins(
                12,
                6,
                10,
                6,
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
            14,
            6,
            10,
            6,
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
        margen_izquierdo: int = 44,
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
            32,
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

        self._etiqueta = etiqueta

    def set_activo(
        self,
        activo: bool,
    ) -> None:

        nombre = (
            "BotonSubmoduloActivo"
            if activo
            else "BotonSubmodulo"
        )

        if self.objectName() == nombre:

            return

        self.setObjectName(
            nombre,
        )

        for widget in (
            self,
            self._etiqueta,
        ):

            widget.style().unpolish(
                widget,
            )

            widget.style().polish(
                widget,
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
