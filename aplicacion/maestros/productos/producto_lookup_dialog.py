from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel,
)

from aplicacion.framework.lookup.lookup_dialog import (
    LookupDialog,
)
from aplicacion.maestros.productos.producto_dialogo import (
    abrir_dialogo_nuevo_producto,
    producto_a_lookup_result,
)
from aplicacion.maestros.productos.producto_lookup import (
    ProductoLookup,
)
from aplicacion.recursos.ui.botones import Botones


class ProductoLookupDialog(LookupDialog):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            ProductoLookup(),
            titulo="Buscar producto",
            parent=parent,
        )

    def _crear_ui(self):

        super()._crear_ui()

        self.txt_buscar.setPlaceholderText(
            "Nombre, código de producto o código de barras",
        )

        self.lbl_sin_resultados = QLabel(
            "",
        )

        self.lbl_sin_resultados.setStyleSheet(
            "color: #546e7a; padding: 4px 0;",
        )

        self.layout().insertWidget(
            2,
            self.lbl_sin_resultados,
        )

        botones = self.layout().itemAt(
            self.layout().count() - 1,
        ).layout()

        self.btn_crear = Botones.nuevo()

        self.btn_crear.setText(
            "Crear producto",
        )

        botones.insertWidget(
            0,
            self.btn_crear,
        )

        self.btn_crear.clicked.connect(
            self._crear_producto,
        )

    def _texto_busqueda(self) -> str:

        return (
            self.txt_buscar
            .text()
            .strip()
        )

    def _actualizar_aviso(
        self,
    ) -> None:

        if not hasattr(
            self,
            "lbl_sin_resultados",
        ):

            return

        if self.tabla.rowCount():

            self.lbl_sin_resultados.setText(
                "",
            )

            return

        texto = self._texto_busqueda()

        if texto:

            self.lbl_sin_resultados.setText(
                f'No hay coincidencias para "{texto}". '
                "Use «Crear producto» para registrarlo."
            )

            return

        self.lbl_sin_resultados.setText(
            "Escriba para buscar o use «Crear producto».",
        )

    def _cargar(self):

        super()._cargar()

        self._actualizar_aviso()

    def _buscar(self):

        super()._buscar()

        self._actualizar_aviso()

    def _crear_producto(self):

        producto = abrir_dialogo_nuevo_producto(

            parent=self.window(),

            nombre_inicial=self._texto_busqueda(),

        )

        if producto is None:

            return

        self.seleccionar(
            producto_a_lookup_result(
                producto,
            ),
        )
