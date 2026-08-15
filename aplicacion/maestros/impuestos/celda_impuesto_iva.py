from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QWidget,
)

from aplicacion.maestros.impuestos.iva_catalogo import (
    CODIGO_IVA_PREDETERMINADO,
    OPCIONES_IVA,
    indice_por_codigo,
)
from aplicacion.maestros.impuestos.repositorio import (
    RepositorioImpuesto,
)


class CeldaImpuestoIVA(
    QWidget,
):

    def __init__(
        self,
        impuesto_id=None,
        parent=None,
    ):

        super().__init__(
            parent,
        )

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
            95,
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

            self._seleccionar_codigo(
                CODIGO_IVA_PREDETERMINADO,
            )

    def _cargar_opciones(
        self,
    ) -> None:

        self.combo.clear()

        self._indice_por_id.clear()

        for indice, (
            codigo,
            etiqueta,
        ) in enumerate(
            OPCIONES_IVA,
        ):

            impuesto = RepositorioImpuesto.obtener_por_codigo(
                codigo,
            )

            impuesto_id = (
                impuesto.id
                if impuesto is not None
                else None
            )

            self.combo.addItem(
                etiqueta,
                impuesto_id,
            )

            if impuesto_id is not None:

                self._indice_por_id[
                    impuesto_id
                ] = indice

    def _on_cambio(
        self,
        _indice: int,
    ) -> None:

        self.impuesto_id = self.combo.currentData()

    def _seleccionar_codigo(
        self,
        codigo: str,
    ) -> None:

        indice = indice_por_codigo(
            codigo,
        )

        self.combo.setCurrentIndex(
            indice,
        )

        self.impuesto_id = self.combo.currentData()

    def _cargar_por_id(
        self,
        impuesto_id,
    ) -> None:

        if impuesto_id is None:

            self._seleccionar_codigo(
                CODIGO_IVA_PREDETERMINADO,
            )

            return

        indice = self._indice_por_id.get(
            impuesto_id,
        )

        if indice is None:

            impuesto = RepositorioImpuesto.obtener_por_id(
                impuesto_id,
            )

            if impuesto is not None:

                self._seleccionar_codigo(
                    str(
                        impuesto.codigo
                        or "",
                    ),
                )

                return

            self._seleccionar_codigo(
                CODIGO_IVA_PREDETERMINADO,
            )

            return

        self.combo.setCurrentIndex(
            indice,
        )

        self.impuesto_id = impuesto_id

    def valor(
        self,
    ):

        return self.combo.currentData()
