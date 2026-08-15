from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QWidget,
)

from aplicacion.maestros.impuestos.repositorio import (
    RepositorioImpuesto,
)


class CeldaRetencionCombo(
    QWidget,
):

    cambiado = Signal()

    def __init__(
        self,
        lookup,
        impuesto_id=None,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self._lookup = lookup
        self.impuesto_id = impuesto_id

        layout = QHBoxLayout(
            self,
        )

        layout.setContentsMargins(
            4,
            2,
            4,
            2,
        )

        self.combo = QComboBox()

        self.combo.setMinimumWidth(
            130,
        )

        self._indice_por_id: dict[
            object,
            int,
        ] = {}

        self._cargar_opciones()

        layout.addWidget(
            self.combo,
        )

        self.combo.currentIndexChanged.connect(
            self._on_cambio,
        )

        if impuesto_id is not None:

            self._cargar_por_id(
                impuesto_id,
            )

        else:

            self._seleccionar_vacio()

    def _cargar_opciones(
        self,
    ) -> None:

        self.combo.clear()

        self._indice_por_id.clear()

        self.combo.addItem(
            "— Sin retención —",
            None,
        )

        items = self._lookup.buscar(
            "",
        )

        items.sort(
            key=lambda resultado: float(
                getattr(
                    getattr(
                        resultado,
                        "objeto",
                        None,
                    ),
                    "porcentaje",
                    0,
                )
                or 0,
            ),
        )

        for indice, resultado in enumerate(
            items,
            start=1,
        ):

            self.combo.addItem(
                resultado.texto,
                resultado.valor,
            )

            self._indice_por_id[
                resultado.valor
            ] = indice

    def _on_cambio(
        self,
        _indice: int,
    ) -> None:

        self.impuesto_id = self.combo.currentData()

        self.cambiado.emit()

    def _seleccionar_vacio(
        self,
    ) -> None:

        self.combo.setCurrentIndex(
            0,
        )

        self.impuesto_id = None

    def _cargar_por_codigo(
        self,
        codigo: str,
    ) -> None:

        codigo = str(
            codigo or "",
        ).strip().upper()

        if not codigo:

            self._seleccionar_vacio()

            return

        impuesto = RepositorioImpuesto.obtener_por_codigo(
            codigo,
        )

        if impuesto is None:

            self._seleccionar_vacio()

            return

        self._cargar_por_id(
            impuesto.id,
        )

    def _cargar_por_id(
        self,
        impuesto_id,
    ) -> None:

        if impuesto_id in (
            None,
            "",
            0,
            "0",
        ):

            self._seleccionar_vacio()

            return

        indice = self._indice_por_id.get(
            impuesto_id,
        )

        if indice is None:

            impuesto = RepositorioImpuesto.obtener_por_id(
                impuesto_id,
            )

            if impuesto is not None:

                self._cargar_por_codigo(
                    str(
                        impuesto.codigo
                        or "",
                    ),
                )

                return

            self._seleccionar_vacio()

            return

        self.combo.setCurrentIndex(
            indice,
        )

        self.impuesto_id = impuesto_id

    def valor(
        self,
    ):

        return self.combo.currentData()
