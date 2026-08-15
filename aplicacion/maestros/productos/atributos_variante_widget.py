from __future__ import annotations

import re
import unicodedata

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from aplicacion.recursos.ui.botones import Botones


def normalizar_clave_atributo(
    nombre: str,
) -> str:

    texto = unicodedata.normalize(
        "NFKD",
        str(nombre or "").strip(),
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(
            caracter,
        )
    )

    texto = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        texto,
    ).strip("_").lower()

    return texto or "atributo"


class AtributosVarianteWidget(QWidget):

    cambio = Signal()

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self._crear_ui()

    def _crear_ui(self):

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        ayuda = QLabel(
            "Atributos adicionales por variante "
            "(ej. material, presentación). "
            "Aparecerán como columnas en la tabla.",
        )

        ayuda.setWordWrap(
            True,
        )

        ayuda.setStyleSheet(
            "color: #546e7a; padding-bottom: 4px;",
        )

        layout.addWidget(
            ayuda,
        )

        fila = QHBoxLayout()

        self.editor = QLineEdit()

        self.editor.setPlaceholderText(
            "Nombre del atributo",
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

        self.lista.setMaximumHeight(
            90,
        )

        layout.addWidget(
            self.lista,
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

    def _agregar(self):

        nombre = self.editor.text().strip()

        if not nombre:

            return

        clave = normalizar_clave_atributo(
            nombre,
        )

        for indice in range(
            self.lista.count(),
        ):

            item = self.lista.item(
                indice,
            )

            if item.data(
                256,
            ) == clave:

                self.editor.clear()

                return

        self.lista.addItem(
            nombre,
        )

        item = self.lista.item(
            self.lista.count() - 1,
        )

        item.setData(
            256,
            clave,
        )

        self.editor.clear()

        self.cambio.emit()

    def _quitar(self):

        fila = self.lista.currentRow()

        if fila < 0:

            return

        self.lista.takeItem(
            fila,
        )

        self.cambio.emit()

    def cargar(
        self,
        nombres: list[str] | None,
    ):

        self.lista.clear()

        vistos = set()

        for nombre in nombres or []:

            texto = str(
                nombre or "",
            ).strip()

            if not texto:

                continue

            clave = normalizar_clave_atributo(
                texto,
            )

            if clave in vistos:

                continue

            vistos.add(
                clave,
            )

            self.lista.addItem(
                texto,
            )

            item = self.lista.item(
                self.lista.count() - 1,
            )

            item.setData(
                256,
                clave,
            )

    def obtener_definiciones(
        self,
    ) -> list[dict]:

        definiciones = []

        for indice in range(
            self.lista.count(),
        ):

            item = self.lista.item(
                indice,
            )

            nombre = item.text().strip()

            clave = item.data(
                256,
            ) or normalizar_clave_atributo(
                nombre,
            )

            definiciones.append(
                {
                    "nombre": nombre,
                    "clave": clave,
                },
            )

        return definiciones

    def obtener_nombres(
        self,
    ) -> list[str]:

        return [
            item["nombre"]
            for item in self.obtener_definiciones()
        ]

    def obtener_claves(
        self,
    ) -> list[str]:

        return [
            item["clave"]
            for item in self.obtener_definiciones()
        ]
