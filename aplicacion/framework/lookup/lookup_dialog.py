from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
)

from aplicacion.framework.lookup.lookup_table import LookupTable
from aplicacion.recursos.ui.botones import Botones


class LookupDialog(QDialog):

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        datasource,
        titulo="Buscar",
        parent=None,
    ):

        super().__init__(parent)

        self.datasource = datasource

        self.resultado = None

        self.setWindowTitle(
            titulo
        )

        self.resize(
            700,
            500,
        )

        self._crear_ui()

        self._conectar_eventos()

        self._cargar()

        self.txt_buscar.setFocus()


    # =====================================================
    # Crear UI
    # =====================================================

    def _crear_ui(self):

        layout = QVBoxLayout(self)

        # ------------------------------------
        # Buscar
        # ------------------------------------

        fila = QHBoxLayout()

        fila.addWidget(
            QLabel("Buscar:")
        )

        self.txt_buscar = QLineEdit()

        fila.addWidget(
            self.txt_buscar
        )

        layout.addLayout(
            fila
        )

        # ------------------------------------
        # Tabla
        # ------------------------------------

        self.tabla = LookupTable()

        layout.addWidget(
            self.tabla
        )

        # ------------------------------------
        # Botones
        # ------------------------------------

        botones = QHBoxLayout()

        botones.addStretch()

        self.btn_aceptar = Botones.aceptar()

        self.btn_cancelar = Botones.cancelar()

        botones.addWidget(
            self.btn_aceptar
        )

        botones.addWidget(
            self.btn_cancelar
        )

        layout.addLayout(
            botones
        )


    # =====================================================
    # Eventos
    # =====================================================

    def _conectar_eventos(self):

        self.txt_buscar.textChanged.connect(
            self._buscar
        )

        self.txt_buscar.returnPressed.connect(
            self._aceptar
        )

        self.btn_cancelar.clicked.connect(
            self.reject
        )

        self.btn_aceptar.clicked.connect(
            self._aceptar
        )

        self.tabla.doubleClicked.connect(
            self._aceptar
        )


    # =====================================================
    # Cargar resultados
    # =====================================================

    def _cargar(self):

        resultados = self.datasource.buscar()

        self.tabla.cargar(
            resultados
        )

        if self.tabla.rowCount():

            self.tabla.selectRow(
                0
            )


    # =====================================================
    # Buscar
    # =====================================================

    def _buscar(self):

        resultados = self.datasource.buscar(
            self.txt_buscar.text()
        )

        self.tabla.cargar(
            resultados
        )

        if self.tabla.rowCount():

            self.tabla.selectRow(
                0
            )


    # =====================================================
    # Aceptar
    # =====================================================

    def _aceptar(self):

        resultado = self.tabla.resultado_seleccionado()

        if resultado is None:

            return

        self.seleccionar(
            resultado
        )


    # =====================================================
    # Seleccionar
    # =====================================================

    def seleccionar(
        self,
        resultado,
    ):

        self.resultado = resultado

        self.accept()