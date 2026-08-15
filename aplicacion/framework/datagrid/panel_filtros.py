from __future__ import annotations

from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from aplicacion.framework.datagrid.filtros import (
    BooleanFilter,
    ComboFilter,
    DateRangeFilter,
    FiltroBase,
    LookupFilter,
    TextFilter,
)
from aplicacion.framework.datagrid.lookup_filter_widget import (
    LookupFilterWidget,
)


class PanelFiltros(QWidget):
    """
    Panel declarativo de filtros para maestros CRUD.
    """

    aplicar = Signal()
    limpiar = Signal()

    def __init__(
        self,
        definiciones: list[FiltroBase],
        *,
        campos_ocultos: set[str] | None = None,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.definiciones = [
            definicion
            for definicion in definiciones
            if definicion.campo
            not in (
                campos_ocultos or set()
            )
        ]

        self._widgets: dict[
            str,
            QWidget,
        ] = {}

        self._crear_ui()

    def _crear_ui(
        self,
    ) -> None:

        layout = QHBoxLayout(
            self,
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            8,
        )

        for definicion in self.definiciones:

            layout.addWidget(
                QLabel(
                    f"{definicion.etiqueta}:",
                ),
            )

            widget = self._crear_widget(
                definicion,
            )

            self._widgets[
                definicion.campo
            ] = widget

            layout.addWidget(
                widget,
            )

        layout.addStretch(
            1,
        )

        btn_aplicar = QPushButton(
            "Filtrar",
        )

        btn_aplicar.clicked.connect(
            self.aplicar.emit,
        )

        layout.addWidget(
            btn_aplicar,
        )

        btn_limpiar = QPushButton(
            "Limpiar",
        )

        btn_limpiar.clicked.connect(
            self._on_limpiar,
        )

        layout.addWidget(
            btn_limpiar,
        )

    def _crear_widget(
        self,
        definicion: FiltroBase,
    ) -> QWidget:

        if isinstance(
            definicion,
            TextFilter,
        ):

            campo = QLineEdit()

            campo.setPlaceholderText(
                definicion.etiqueta,
            )

            campo.returnPressed.connect(
                self.aplicar.emit,
            )

            return campo

        if isinstance(
            definicion,
            ComboFilter,
        ):

            combo = QComboBox()

            combo.addItem(
                "Todos",
                "",
            )

            for valor, etiqueta in definicion.opciones:

                combo.addItem(
                    etiqueta,
                    valor,
                )

            return combo

        if isinstance(
            definicion,
            BooleanFilter,
        ):

            combo = QComboBox()

            combo.addItem(
                "Todos",
                None,
            )

            combo.addItem(
                "Sí",
                True,
            )

            combo.addItem(
                "No",
                False,
            )

            return combo

        if isinstance(
            definicion,
            DateRangeFilter,
        ):

            contenedor = QWidget()

            layout_fechas = QHBoxLayout(
                contenedor,
            )

            layout_fechas.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            desde = QLineEdit()

            desde.setPlaceholderText(
                "Desde",
            )

            hasta = QLineEdit()

            hasta.setPlaceholderText(
                "Hasta",
            )

            layout_fechas.addWidget(
                desde,
            )

            layout_fechas.addWidget(
                hasta,
            )

            contenedor.desde_edit = desde
            contenedor.hasta_edit = hasta

            return contenedor

        if isinstance(
            definicion,
            LookupFilter,
        ):

            widget = LookupFilterWidget(
                placeholder=definicion.placeholder,
                lookup=definicion.lookup,
            )

            widget.cambiado.connect(
                self.aplicar.emit,
            )

            return widget

        campo = QLineEdit()

        return campo

    @staticmethod
    def _parse_fecha(
        texto: str,
    ):

        from datetime import datetime

        texto = str(
            texto or "",
        ).strip()

        if not texto:

            return None

        for formato in (
            "%d/%m/%Y",
            "%Y-%m-%d",
        ):

            try:

                return datetime.strptime(
                    texto,
                    formato,
                ).date()

            except ValueError:

                continue

        return None

    def valores(
        self,
    ) -> dict[str, Any]:

        resultado: dict[
            str,
            Any,
        ] = {}

        for definicion in self.definiciones:

            widget = self._widgets.get(
                definicion.campo,
            )

            if widget is None:

                continue

            if isinstance(
                widget,
                LookupFilterWidget,
            ):

                resultado[
                    definicion.campo
                ] = widget.valor()

                continue

            if isinstance(
                definicion,
                DateRangeFilter,
            ) and hasattr(
                widget,
                "desde_edit",
            ):

                resultado[
                    definicion.campo
                ] = {
                    "desde": self._parse_fecha(
                        widget.desde_edit.text(),
                    ),
                    "hasta": self._parse_fecha(
                        widget.hasta_edit.text(),
                    ),
                }

                continue

            if isinstance(
                widget,
                QLineEdit,
            ):

                resultado[
                    definicion.campo
                ] = widget.text()

            elif isinstance(
                widget,
                QComboBox,
            ):

                resultado[
                    definicion.campo
                ] = widget.currentData()

            elif isinstance(
                widget,
                QCheckBox,
            ):

                resultado[
                    definicion.campo
                ] = widget.isChecked()

        return resultado

    def _on_limpiar(
        self,
    ) -> None:

        for definicion in self.definiciones:

            widget = self._widgets.get(
                definicion.campo,
            )

            if widget is None:

                continue

            if isinstance(
                widget,
                LookupFilterWidget,
            ):

                widget.limpiar()

                continue

            if isinstance(
                definicion,
                DateRangeFilter,
            ) and hasattr(
                widget,
                "desde_edit",
            ):

                widget.desde_edit.clear()
                widget.hasta_edit.clear()

                continue

            if isinstance(
                widget,
                QLineEdit,
            ):

                widget.clear()

            elif isinstance(
                widget,
                QComboBox,
            ):

                widget.setCurrentIndex(
                    0,
                )

            elif isinstance(
                widget,
                QCheckBox,
            ):

                widget.setChecked(
                    False,
                )

        self.limpiar.emit()
