"""
Barra de teclas de función (idea de Sysplus): abajo de la ventana se
ven siempre las teclas que sirven en la pantalla actual, por ejemplo
"F10 Guardar · F3 Cliente · F4 Producto". Cada una también se puede
pulsar con el mouse.

Cada pantalla publica sus teclas con un método ``teclas_contexto()``
que devuelve una lista de ``(tecla, texto, función)``. La barra busca
ese método en la pestaña activa; si no lo encuentra muestra las teclas
generales.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


def proveedor_teclas(
    widget,
):
    """El widget de la pestaña (o un hijo) que publica sus teclas."""

    if widget is None:

        return None

    if callable(
        getattr(
            widget,
            "teclas_contexto",
            None,
        ),
    ):

        return widget

    for hijo in widget.findChildren(
        QWidget,
    ):

        if callable(
            getattr(
                hijo,
                "teclas_contexto",
                None,
            ),
        ):

            return hijo

    return None


class BotonTecla(QPushButton):

    def __init__(
        self,
        tecla: str,
        texto: str,
        accion=None,
    ):

        super().__init__()

        self.setObjectName(
            "BotonTecla",
        )

        self.setFocusPolicy(
            Qt.NoFocus,
        )

        self.setCursor(
            Qt.PointingHandCursor,
        )

        self.setSizePolicy(
            QSizePolicy.Maximum,
            QSizePolicy.Fixed,
        )

        layout = QHBoxLayout(
            self,
        )

        layout.setContentsMargins(
            4,
            0,
            8,
            0,
        )

        layout.setSpacing(
            5,
        )

        self.lbl_tecla = QLabel(
            tecla,
        )

        self.lbl_tecla.setObjectName(
            "TeclaTapa",
        )

        self.lbl_tecla.setAlignment(
            Qt.AlignCenter,
        )

        self.lbl_texto = QLabel(
            texto,
        )

        self.lbl_texto.setObjectName(
            "TeclaTexto",
        )

        layout.addWidget(
            self.lbl_tecla,
        )

        layout.addWidget(
            self.lbl_texto,
        )

        self.setMinimumWidth(
            self.lbl_tecla.sizeHint().width()
            + self.lbl_texto.sizeHint().width()
            + 22,
        )

        self.tecla = tecla
        self.texto = texto

        if accion is None:

            self.setEnabled(
                False,
            )

        else:

            self.clicked.connect(
                lambda _=False: accion(),
            )


class BarraTeclas(QWidget):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "BarraTeclas",
        )

        habilitar_fondo_qss(
            self,
        )

        self.setFixedHeight(
            30,
        )

        self._layout = QHBoxLayout(
            self,
        )

        self._layout.setContentsMargins(
            6,
            3,
            6,
            3,
        )

        self._layout.setSpacing(
            2,
        )

        self._generales: list = []

        self.botones: list[BotonTecla] = []

    def set_teclas_generales(
        self,
        teclas,
    ) -> None:

        self._generales = list(
            teclas,
        )

    def mostrar(
        self,
        teclas,
    ) -> None:

        while self._layout.count():

            item = self._layout.takeAt(
                0,
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

        self.botones = []

        for tecla, texto, accion in list(
            teclas or [],
        ):

            boton = BotonTecla(
                tecla,
                texto,
                accion,
            )

            self.botones.append(
                boton,
            )

            self._layout.addWidget(
                boton,
            )

        self._layout.addStretch(
            1,
        )

    def actualizar_desde(
        self,
        widget,
    ) -> None:
        """Muestra las teclas de la pestaña ``widget``."""

        proveedor = proveedor_teclas(
            widget,
        )

        teclas = []

        if proveedor is not None:

            try:

                teclas = list(
                    proveedor.teclas_contexto() or [],
                )

            except Exception:

                teclas = []

        self.mostrar(
            teclas
            + self._generales,
        )
