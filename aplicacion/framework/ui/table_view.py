from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableView,
)


class TableView(QTableView):
    """
    Vista de tabla base del Framework (QTableView).
    """

    def __init__(self):

        super().__init__()

        self._configurar()

    def _configurar(self):

        self._configurar_seleccion()
        self._configurar_apariencia()
        self._configurar_encabezados()
        self._configurar_scroll()
        self._configurar_estilos()

    def _configurar_seleccion(self):

        self.setSelectionBehavior(
            QAbstractItemView.SelectRows,
        )

        self.setSelectionMode(
            QAbstractItemView.SingleSelection,
        )

        self.setEditTriggers(
            QAbstractItemView.NoEditTriggers,
        )

        self.setFocusPolicy(
            Qt.StrongFocus,
        )

    def _configurar_apariencia(self):

        self.setAlternatingRowColors(
            True,
        )

        self.setSortingEnabled(
            True,
        )

        self.setShowGrid(
            False,
        )

        self.setWordWrap(
            False,
        )

        self.setCornerButtonEnabled(
            False,
        )

        self.setContextMenuPolicy(
            Qt.CustomContextMenu,
        )

        self.setMouseTracking(
            True,
        )

    def _configurar_encabezados(self):

        self.verticalHeader().setVisible(
            False,
        )

        self.verticalHeader().setDefaultSectionSize(
            38,
        )

        header = self.horizontalHeader()

        header.setStretchLastSection(
            True,
        )

        header.setMinimumHeight(
            42,
        )

        header.setDefaultAlignment(
            Qt.AlignCenter,
        )

        header.setHighlightSections(
            False,
        )

        header.setSectionResizeMode(
            QHeaderView.Interactive,
        )

    def _configurar_scroll(self):

        self.setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel,
        )

        self.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel,
        )

    def _configurar_estilos(self):

        self.setStyleSheet(
            """
            QTableView{
                background:#FFFFFF;
                color:#1E293B;
                border:1px solid #AEB8C5;
                border-radius:2px;
                alternate-background-color:#F4F6F9;
                selection-background-color:#C9D9EC;
                selection-color:#1E293B;
                font-size:13px;
                outline:none;
            }
            QTableView::item{
                padding:3px 6px;
                border:none;
            }
            QTableView::item:selected{
                background:#C9D9EC;
                color:#1E293B;
            }
            QTableView::item:hover{
                background:#F8FAFC;
            }
            QHeaderView::section{
                background:#C9D2DD;
                color:#1E293B;
                border:none;
                border-right:1px solid #B8C2CE;
                border-bottom:1px solid #AEB8C5;
                padding:5px 6px;
                font-size:13px;
                font-weight:600;
            }
            QHeaderView::section:last{
                border-right:none;
            }
            """
        )

    def rowCount(self) -> int:

        modelo = self.model()

        if modelo is None:

            return 0

        return modelo.rowCount()
