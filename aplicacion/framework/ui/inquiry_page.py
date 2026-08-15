from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTableWidget,
)

from aplicacion.comunes.exportacion import (
    boton_exportar_excel,
)
from aplicacion.framework.base.page import Page


class InquiryPage(Page):
    """
    Página base para consultas con filtros y tabla de resultados.
    """

    _COLUMNAS: list[str] = []
    _NOMBRE_EXPORT: str = ""
    _TITULO_BOTON = "Consultar"

    def _crear_ui(self) -> None:

        super()._crear_ui()

        self._layout_filtros = QHBoxLayout()

        self._crear_filtros()

        self._agregar_botones_filtro()

        self._btn_consultar = QPushButton(
            self._TITULO_BOTON,
        )

        self._btn_consultar.clicked.connect(
            self._consultar,
        )

        self._layout_filtros.addWidget(
            self._btn_consultar,
        )

        self.tabla = QTableWidget()

        if self._COLUMNAS:

            self.tabla.setColumnCount(
                len(self._COLUMNAS),
            )

            self.tabla.setHorizontalHeaderLabels(
                self._COLUMNAS,
            )

        if self._NOMBRE_EXPORT:

            self._layout_filtros.addWidget(
                boton_exportar_excel(
                    self.tabla,
                    parent=self,
                    titulo=self._NOMBRE_EXPORT,
                ),
            )

        self._layout_filtros.addStretch()

        self.agregar_layout(
            self._layout_filtros,
        )

        self.agregar_widget(
            self.tabla,
        )

    def _crear_filtros(self) -> None:
        """
        Las subclases agregan controles a ``self._layout_filtros``.
        """

    def _agregar_botones_filtro(self) -> None:
        """
        Botones adicionales antes del botón consultar.
        """

    def _consultar(self) -> None:
        pass

    def cargar(self) -> None:

        self._consultar()
