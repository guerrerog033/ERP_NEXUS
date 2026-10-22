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
                border:1px solid #E2E8F0;
                border-radius:8px;
                alternate-background-color:#F8FAFC;
                selection-background-color:#EAF0F7;
                selection-color:#1E293B;
                font-size:13px;
                outline:none;
            }
            QTableView::item{
                padding:8px;
                border:none;
            }
            QTableView::item:selected{
                background:#EAF0F7;
                color:#1E293B;
            }
            QTableView::item:hover{
                background:#F8FAFC;
            }
            QHeaderView::section{
                background:#F8FAFC;
                color:#475569;
                border:none;
                border-bottom:1px solid #E2E8F0;
                padding:9px 8px;
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
