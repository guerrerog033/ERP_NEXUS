from __future__ import annotations

from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtWidgets import (
    QCompleter,
    QHBoxLayout,
    QLineEdit,
    QWidget,
)

from aplicacion.maestros.impuestos.etiquetas import (
    etiqueta_impuesto_resultado,
)
from aplicacion.maestros.impuestos.impuesto_lookup import (
    ImpuestoLookup,
)


class CeldaImpuestoBusqueda(QWidget):

    def __init__(
        self,
        impuesto_id=None,
        texto: str = "",
        parent=None,
        lookup=None,
        placeholder: str = "Buscar impuesto...",
    ):

        super().__init__(
            parent,
        )

        self.impuesto_id = impuesto_id

        self._mapa: dict[str, object] = {}

        self._lookup = lookup or ImpuestoLookup()

        layout = QHBoxLayout(
            self,
        )

        layout.setContentsMargins(
            4,
            2,
            4,
            2,
        )

        self.txt = QLineEdit()

        self.txt.setPlaceholderText(
            placeholder,
        )

        self._completer = QCompleter(
            [],
            self,
        )

        self._completer.setCaseSensitivity(
            Qt.CaseInsensitive,
        )

        self._completer.setFilterMode(
            Qt.MatchContains,
        )

        self._completer.setCompletionMode(
            QCompleter.PopupCompletion,
        )

        self.txt.setCompleter(
            self._completer,
        )

        layout.addWidget(
            self.txt,
        )

        self.txt.textChanged.connect(
            self._on_texto,
        )

        self._completer.activated.connect(
            self._on_seleccion,
        )

        if texto:

            self.txt.setText(
                texto,
            )

        elif impuesto_id is not None:

            self._cargar_por_id(
                impuesto_id,
            )

    def _etiqueta(
        self,
        resultado,
    ) -> str:

        return etiqueta_impuesto_resultado(
            resultado,
        )

    def _on_texto(
        self,
        texto: str,
    ):

        resultados = self._lookup.buscar(
            texto.strip(),
        )

        self._mapa.clear()

        etiquetas = []

        for resultado in resultados:

            etiqueta = self._etiqueta(
                resultado,
            )

            self._mapa[etiqueta] = (
                resultado.valor
            )

            etiquetas.append(
                etiqueta,
            )

        self._completer.setModel(
            QStringListModel(
                etiquetas,
            ),
        )

        if texto.strip():

            self._completer.complete()

        elif not self._mapa:

            self.impuesto_id = None

    def _on_seleccion(
        self,
        texto,
    ):

        self.impuesto_id = self._mapa.get(
            str(
                texto,
            ),
        )

    def _cargar_por_id(
        self,
        impuesto_id,
    ):

        resultado = self._lookup.buscar_por_id(
            impuesto_id,
        )

        if resultado is None:

            return

        self.impuesto_id = resultado.valor

        self.txt.setText(
            self._etiqueta(
                resultado,
            ),
        )

    def valor(self):

        texto = self.txt.text().strip()

        if (
            texto
            and texto in self._mapa
        ):

            self.impuesto_id = self._mapa[
                texto
            ]

        return self.impuesto_id
