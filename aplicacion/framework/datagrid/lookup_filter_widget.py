from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)

from aplicacion.framework.lookup.lookup_dialog import (
    LookupDialog,
)
from aplicacion.recursos.ui.botones import Botones


class LookupFilterWidget(QWidget):
    """
    Widget compacto de filtro lookup con diálogo de búsqueda.
    """

    cambiado = Signal()

    def __init__(
        self,
        *,
        placeholder: str = "Buscar…",
        lookup=None,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self._lookup_cls = lookup
        self._valor = None

        layout = QHBoxLayout(
            self,
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            4,
        )

        self.txt = QLineEdit()

        self.txt.setReadOnly(
            True,
        )

        self.txt.setPlaceholderText(
            placeholder,
        )

        self.btn = Botones.buscar()

        layout.addWidget(
            self.txt,
        )

        layout.addWidget(
            self.btn,
        )

        self.btn.clicked.connect(
            self._abrir_dialogo,
        )

    def _datasource(
        self,
    ):

        if self._lookup_cls is None:

            return None

        if callable(
            self._lookup_cls,
        ):

            return self._lookup_cls()

        return self._lookup_cls

    def _abrir_dialogo(
        self,
    ) -> None:

        datasource = self._datasource()

        if datasource is None:

            return

        dialogo = LookupDialog(
            datasource=datasource,
            parent=self,
        )

        if dialogo.exec():

            self.establecer(
                dialogo.resultado,
            )

            self.cambiado.emit()

    def establecer(
        self,
        resultado,
    ) -> None:

        self._valor = resultado

        if resultado is None:

            self.txt.clear()

            return

        codigo = getattr(
            resultado,
            "codigo",
            "",
        )

        texto = getattr(
            resultado,
            "texto",
            "",
        )

        if codigo:

            self.txt.setText(
                f"{codigo} - {texto}",
            )

        else:

            self.txt.setText(
                str(
                    texto,
                ),
            )

    def valor(
        self,
    ):

        if self._valor is None:

            return None

        return getattr(
            self._valor,
            "valor",
            self._valor,
        )

    def limpiar(
        self,
    ) -> None:

        self._valor = None

        self.txt.clear()
