from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from aplicacion.framework.menu_manifest import (
    MODULO_PENDIENTE,
    ResultadoBusqueda,
    buscar_modulos,
    modulo_accesible,
)
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


class BuscadorModulos(QDialog):

    modulo_seleccionado = Signal(str)

    def __init__(
        self,
        texto_inicial: str = "",
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "BuscadorModulos",
        )

        habilitar_fondo_qss(
            self,
        )

        self.setWindowTitle(
            "Buscar módulo",
        )

        self.setMinimumSize(
            520,
            380,
        )

        self._resultados: list[
            ResultadoBusqueda
        ] = []

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        layout.setSpacing(
            10,
        )

        self.txt_busqueda = QLineEdit()

        self.txt_busqueda.setObjectName(
            "BuscadorModulosEntrada",
        )

        self.txt_busqueda.setPlaceholderText(
            "Escriba para buscar procesos, maestros o informes...",
        )

        self.txt_busqueda.setClearButtonEnabled(
            True,
        )

        self.txt_busqueda.setText(
            texto_inicial,
        )

        self.lbl_ayuda = QLabel(
            "Enter para abrir · Doble clic para abrir",
        )

        self.lbl_ayuda.setObjectName(
            "BuscadorModulosAyuda",
        )

        self.lista = QListWidget()

        self.lista.setObjectName(
            "BuscadorModulosLista",
        )

        botones = QHBoxLayout()

        self.btn_abrir = QPushButton(
            "Abrir",
        )

        self.btn_abrir.setObjectName(
            "BotonRapidoDestacado",
        )

        self.btn_cancelar = QPushButton(
            "Cancelar",
        )

        botones.addStretch()

        botones.addWidget(
            self.btn_cancelar,
        )

        botones.addWidget(
            self.btn_abrir,
        )

        layout.addWidget(
            self.txt_busqueda,
        )

        layout.addWidget(
            self.lbl_ayuda,
        )

        layout.addWidget(
            self.lista,
            1,
        )

        layout.addLayout(
            botones,
        )

        self.txt_busqueda.textChanged.connect(
            self._filtrar,
        )

        self.txt_busqueda.returnPressed.connect(
            self._abrir_seleccion,
        )

        self.lista.itemActivated.connect(
            self._abrir_item,
        )

        self.lista.itemDoubleClicked.connect(
            self._abrir_item,
        )

        self.btn_abrir.clicked.connect(
            self._abrir_seleccion,
        )

        self.btn_cancelar.clicked.connect(
            self.reject,
        )

        self._filtrar(
            texto_inicial,
        )

        self.txt_busqueda.setFocus()

        self.txt_busqueda.selectAll()

    def _filtrar(
        self,
        texto: str = "",
    ) -> None:

        if not isinstance(
            texto,
            str,
        ):

            texto = self.txt_busqueda.text()

        self._resultados = buscar_modulos(
            texto,
        )

        self.lista.clear()

        for indice, resultado in enumerate(
            self._resultados,
        ):

            etiqueta = (
                f"{resultado.titulo}"
            )

            if resultado.pendiente:

                etiqueta += (
                    "  ·  Próximamente"
                )

            item = QListWidgetItem(
                etiqueta,
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                resultado.modulo_id,
            )

            item.setToolTip(
                f"{resultado.grupo}\n{resultado.ruta}",
            )

            if (
                resultado.pendiente
                or resultado.modulo_id
                == MODULO_PENDIENTE
            ):

                item.setFlags(
                    item.flags()
                    & ~Qt.ItemFlag.ItemIsEnabled,
                )

            elif not modulo_accesible(
                str(
                    resultado.modulo_id,
                ),
            ):

                item.setFlags(
                    item.flags()
                    & ~Qt.ItemFlag.ItemIsEnabled,
                )

            self.lista.addItem(
                item,
            )

            if indice == 0:

                self.lista.setCurrentItem(
                    item,
                )

    def _abrir_item(
        self,
        item: QListWidgetItem,
    ) -> None:

        modulo_id = item.data(
            Qt.ItemDataRole.UserRole,
        )

        if not modulo_id:

            return

        if (
            modulo_id
            == MODULO_PENDIENTE
        ):

            return

        if not modulo_accesible(
            str(
                modulo_id,
            ),
        ):

            return

        self.modulo_seleccionado.emit(
            str(
                modulo_id,
            ),
        )

        self.accept()

    def _abrir_seleccion(
        self,
    ) -> None:

        item = self.lista.currentItem()

        if item is None:

            if self._resultados:

                self.modulo_seleccionado.emit(
                    self._resultados[
                        0
                    ].modulo_id,
                )

                self.accept()

            return

        self._abrir_item(
            item,
        )
