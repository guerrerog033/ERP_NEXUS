from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
)

from aplicacion.maestros.productos.atributos_variante_widget import (
    AtributosVarianteWidget,
)
from aplicacion.maestros.productos.variantes_widget import (
    VariantesProductoWidget,
)


class DialogoVariantesProducto(
    QDialog,
):

    def __init__(
        self,
        *,
        definiciones: list[dict] | None = None,
        filas: list[dict] | None = None,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setWindowTitle(
            "Variantes del producto",
        )

        self.resize(
            980,
            620,
        )

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            16,
            16,
            16,
            12,
        )

        layout.setSpacing(
            12,
        )

        self.atributos_widget = (
            AtributosVarianteWidget()
        )

        self.variantes_widget = (
            VariantesProductoWidget()
        )

        self.atributos_widget.cambio.connect(
            self._sincronizar_atributos,
        )

        definiciones = list(
            definiciones or [],
        )

        self.atributos_widget.cargar(
            [
                item["nombre"]
                if isinstance(
                    item,
                    dict,
                )
                else str(
                    item,
                )
                for item in definiciones
            ],
        )

        if (
            definiciones
            and isinstance(
                definiciones[0],
                dict,
            )
        ):

            attrs = definiciones

        else:

            attrs = (
                self.atributos_widget.obtener_definiciones()
            )

        self.variantes_widget.establecer_atributos(
            attrs,
        )

        self.variantes_widget.cargar_filas(
            filas or [],
        )

        layout.addWidget(
            self.atributos_widget,
        )

        layout.addWidget(
            self.variantes_widget,
            1,
        )

        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
        )

        botones.accepted.connect(
            self.accept,
        )

        botones.rejected.connect(
            self.reject,
        )

        layout.addWidget(
            botones,
        )

    def _sincronizar_atributos(
        self,
    ) -> None:

        self.variantes_widget.establecer_atributos(
            self.atributos_widget.obtener_definiciones(),
        )

    def obtener_definiciones(
        self,
    ) -> list[dict]:

        return (
            self.atributos_widget.obtener_definiciones()
        )

    def obtener_filas(
        self,
    ) -> list[dict]:

        return (
            self.variantes_widget.obtener_filas()
        )
