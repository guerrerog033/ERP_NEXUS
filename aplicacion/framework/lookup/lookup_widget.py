from __future__ import annotations

from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
)

from aplicacion.recursos.ui.botones import Botones

from .lookup_dialog import LookupDialog


class LookupWidget(QWidget):

    seleccionado = Signal(object)

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        datasource,
        parent=None,
    ):

        super().__init__(parent)

        self.datasource = datasource

        self.resultado = None

        self._crear_ui()

        self._conectar_eventos()

    # =====================================================
    # UI
    # =====================================================

    def _crear_ui(self):

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.txt = QLineEdit()

        self.txt.setReadOnly(True)

        self.btn = Botones.buscar()

        layout.addWidget(
            self.txt
        )

        layout.addWidget(
            self.btn
        )

    # =====================================================
    # Eventos
    # =====================================================

    def _conectar_eventos(self):

        self.btn.clicked.connect(
            self.buscar
        )

    # =====================================================
    # Buscar
    # =====================================================

    def buscar(self):

        dlg = LookupDialog(
            datasource=self.datasource,
            parent=self,
        )

        if dlg.exec():

            self.establecer(
                dlg.resultado
            )

    # =====================================================
    # Establecer
    # =====================================================

    def establecer(
        self,
        resultado,
    ):

        self.resultado = resultado

        if resultado is None:

            self.txt.clear()

        else:

            self.txt.setText(
                f"{resultado.codigo} - {resultado.texto}"
            )

        self.seleccionado.emit(
            resultado
        )

    # =====================================================
    # Valor
    # =====================================================

    def valor(self):

        if self.resultado is None:

            return None

        return self.resultado.valor

    def value(self):

        return self.valor()

    def setValue(
        self,
        valor,
    ):

        if valor is None:

            self.establecer(
                None,
            )

            return

        resultado = self.datasource.buscar_por_id(
            valor,
        )

        self.establecer(
            resultado,
        )

    # =====================================================
    # Habilitado
    # =====================================================

    def setEnabled(
        self,
        enabled: bool,
    ):

        super().setEnabled(enabled)

        self.txt.setEnabled(enabled)

        self.btn.setEnabled(enabled)