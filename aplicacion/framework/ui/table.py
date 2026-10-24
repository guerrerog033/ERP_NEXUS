from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
)


class Table(QTableWidget):
    """
    Tabla base reutilizable del Framework.

    Encapsula toda la configuración visual
    y de comportamiento de QTableWidget.
    """

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(self):

        super().__init__()

        self._configurar()

    # =====================================================
    # Configuración general
    # =====================================================

    def _configurar(self):

        self._configurar_seleccion()

        self._configurar_apariencia()

        self._configurar_encabezados()

        self._configurar_scroll()

        self._configurar_estilos()

    # =====================================================
    # Selección
    # =====================================================

    def _configurar_seleccion(self):

        self.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.setFocusPolicy(
            Qt.StrongFocus
        )

    # =====================================================
    # Apariencia
    # =====================================================

    def _configurar_apariencia(self):

        self.setAlternatingRowColors(
            True
        )

        self.setSortingEnabled(
            True
        )

        self.setShowGrid(
            False
        )

        self.setWordWrap(
            False
        )

        self.setCornerButtonEnabled(
            False
        )

        self.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.setMouseTracking(
            True
        )

    # =====================================================
    # Encabezados
    # =====================================================

    def _configurar_encabezados(self):

        self.verticalHeader().setVisible(
            False
        )

        self.verticalHeader().setDefaultSectionSize(
            38
        )

        header = self.horizontalHeader()

        header.setStretchLastSection(
            True
        )

        header.setMinimumHeight(
            42
        )

        header.setDefaultAlignment(
            Qt.AlignCenter
        )

        header.setHighlightSections(
            False
        )

        header.setSectionResizeMode(
            QHeaderView.Interactive
        )

    # =====================================================
    # Scroll
    # =====================================================

    def _configurar_scroll(self):

        self.setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )

        self.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel
        )

    # =====================================================
    # Estilos
    # =====================================================

    def _configurar_estilos(self):

        self.setStyleSheet(
            """
            QTableWidget{

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

            QTableWidget::item{

                padding:3px 6px;

                border:none;

            }

            QTableWidget::item:selected{

                background:#C9D9EC;

                color:#1E293B;

            }

            QTableWidget::item:hover{

                background:#EAF0F7;

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

            QScrollBar:vertical{

                background:transparent;

                width:12px;

                margin:2px;

            }

            QScrollBar::handle:vertical{

                background:#CBD5E1;

                border-radius:6px;

                min-height:40px;

            }

            QScrollBar::handle:vertical:hover{

                background:#64748B;

            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical{

                height:0px;

            }

            QScrollBar:horizontal{

                background:transparent;

                height:12px;

                margin:2px;

            }

            QScrollBar::handle:horizontal{

                background:#CBD5E1;

                border-radius:6px;

                min-width:40px;

            }

            QScrollBar::handle:horizontal:hover{

                background:#64748B;

            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal{

                width:0px;

            }
            """
        )