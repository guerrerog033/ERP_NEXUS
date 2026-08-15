from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.base.page import Page
from aplicacion.framework.ui.card import Card
from aplicacion.maestros.productos.catalogo_variantes_servicio import (
    ServicioCatalogoVariantes,
    TIPOS_VARIANTE,
)
from aplicacion.recursos.ui.botones import Botones


class _PanelTipoVariante(QWidget):

    def __init__(
        self,
        tipo: str,
        *,
        nombre_tipo: str = "",
        parent=None,
    ):

        self.tipo = tipo
        self.nombre_tipo = nombre_tipo

        super().__init__(
            parent,
        )

        self._crear_ui()

        self._cargar()

    def _crear_ui(
        self,
    ) -> None:

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            0,
            8,
            0,
            0,
        )

        layout.setSpacing(
            8,
        )

        ayuda = QLabel(
            "Valores disponibles al crear variantes "
            "de productos. Puede escribir valores "
            "nuevos directamente en la tabla del producto.",
        )

        ayuda.setWordWrap(
            True,
        )

        ayuda.setStyleSheet(
            "color:#546e7a;",
        )

        layout.addWidget(
            ayuda,
        )

        fila = QHBoxLayout()

        self.editor = QLineEdit()

        self.editor.setPlaceholderText(
            "Nuevo valor",
        )

        self.editor.returnPressed.connect(
            self._agregar,
        )

        fila.addWidget(
            self.editor,
            1,
        )

        btn_agregar = Botones.nuevo()

        btn_agregar.setText(
            "Agregar",
        )

        btn_agregar.clicked.connect(
            self._agregar,
        )

        fila.addWidget(
            btn_agregar,
        )

        layout.addLayout(
            fila,
        )

        self.lista = QListWidget()

        layout.addWidget(
            self.lista,
            1,
        )

        btn_quitar = Botones.cerrar()

        btn_quitar.setText(
            "Quitar seleccionado",
        )

        btn_quitar.clicked.connect(
            self._quitar,
        )

        layout.addWidget(
            btn_quitar,
        )

        self._items: dict[
            str,
            int,
        ] = {}

    def _cargar(
        self,
    ) -> None:

        self.lista.clear()

        self._items.clear()

        for item in ServicioCatalogoVariantes.listar_por_tipo(
            self.tipo,
            nombre_tipo=self.nombre_tipo,
        ):

            self.lista.addItem(
                item.valor,
            )

            self._items[
                item.valor
            ] = item.id

    def _agregar(
        self,
    ) -> None:

        ok, mensaje = ServicioCatalogoVariantes.crear(
            self.tipo,
            self.editor.text(),
            nombre_tipo=self.nombre_tipo,
        )

        if not ok:

            QMessageBox.warning(
                self,
                "Variantes",
                mensaje,
            )

            return

        self.editor.clear()

        self._cargar()

    def _quitar(
        self,
    ) -> None:

        item = self.lista.currentItem()

        if item is None:

            return

        item_id = self._items.get(
            item.text(),
        )

        if item_id is None:

            return

        ServicioCatalogoVariantes.eliminar(
            item_id,
        )

        self._cargar()


class MaestroCatalogoVariantes(
    Page,
):

    titulo = "Variantes"

    def _crear_ui(
        self,
    ) -> None:

        super()._crear_ui()

        card = Card(
            "Catálogo de variantes",
        )

        card.set_titulo(
            "Catálogo de variantes",
        )

        tabs = QTabWidget()

        for (
            tipo,
            etiqueta,
        ) in TIPOS_VARIANTE.items():

            tabs.addTab(
                _PanelTipoVariante(
                    tipo,
                ),
                etiqueta,
            )

        panel_atributos = QWidget()

        layout_atributos = QVBoxLayout(
            panel_atributos,
        )

        layout_atributos.setContentsMargins(
            0,
            8,
            0,
            0,
        )

        fila_tipo = QHBoxLayout()

        fila_tipo.addWidget(
            QLabel(
                "Nombre del atributo:",
            ),
        )

        self.editor_tipo = QLineEdit()

        self.editor_tipo.setPlaceholderText(
            "Ej. Material, Presentación",
        )

        fila_tipo.addWidget(
            self.editor_tipo,
            1,
        )

        btn_tipo = Botones.nuevo()

        btn_tipo.setText(
            "Agregar tipo",
        )

        btn_tipo.clicked.connect(
            self._agregar_tipo_atributo,
        )

        fila_tipo.addWidget(
            btn_tipo,
        )

        layout_atributos.addLayout(
            fila_tipo,
        )

        self.tabs_atributos = QTabWidget()

        layout_atributos.addWidget(
            self.tabs_atributos,
            1,
        )

        tabs.addTab(
            panel_atributos,
            "Atributos personalizados",
        )

        card.agregar_widget(
            tabs,
        )

        self.agregar_widget(
            card,
        )

        self._cargar_atributos()

    def _cargar_atributos(
        self,
    ) -> None:

        while self.tabs_atributos.count():

            self.tabs_atributos.removeTab(
                0,
            )

        for nombre in ServicioCatalogoVariantes.listar_tipos_atributo():

            self.tabs_atributos.addTab(
                _PanelTipoVariante(
                    "atributo",
                    nombre_tipo=nombre,
                ),
                nombre,
            )

    def _agregar_tipo_atributo(
        self,
    ) -> None:

        nombre = self.editor_tipo.text().strip()

        if not nombre:

            QMessageBox.warning(
                self,
                "Variantes",
                "Indique el nombre del atributo.",
            )

            return

        ok, mensaje = ServicioCatalogoVariantes.crear_tipo_atributo(
            nombre,
        )

        if not ok:

            QMessageBox.warning(
                self,
                "Variantes",
                mensaje,
            )

            return

        self.editor_tipo.clear()

        self._cargar_atributos()

        indice = self.tabs_atributos.count() - 1

        if indice >= 0:

            self.tabs_atributos.setCurrentIndex(
                indice,
            )
