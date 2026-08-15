from __future__ import annotations

from typing import Type

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
)


class CrudDocumento:
    """
    Mixin para maestros cuyo registro se abre
    en vista-documento (preview + acciones).
    """

    vista_documento: Type | None = None

    def usa_vista_documento(
        self,
    ) -> bool:

        return (
            self.vista_documento
            is not None
        )

    def editar(
        self,
    ):

        if not self.usa_vista_documento():

            super().editar()

            return

        id_registro = (
            self.obtener_id_seleccionado()
        )

        if id_registro is None:

            self.mostrar_error(
                "Seleccione un registro.",
            )

            return

        self.abrir_edicion_desde_lista(
            id_registro,
        )

    def consultar(
        self,
    ) -> None:

        if not self.usa_vista_documento():

            super().consultar()

            return

        id_registro = (
            self.obtener_id_seleccionado()
        )

        if id_registro is None:

            self.mostrar_error(
                "Seleccione un registro.",
            )

            return

        self.mostrar_vista_documento(
            id_registro,
        )

    def abrir_edicion_desde_lista(
        self,
        id_registro: int,
    ) -> None:

        self.mostrar_vista_documento(
            id_registro,
        )

    def mostrar_vista_documento(
        self,
        id_registro: int,
    ) -> None:

        if self.vista_documento is None:

            return

        ventana = QDialog(
            self._ventana_padre_vista(),
        )

        ventana.setWindowTitle(
            self._titulo_dialogo_vista(
                id_registro,
            ),
        )

        ventana.setModal(
            True,
        )

        vista = self.vista_documento(
            id_registro=id_registro,
            parent=ventana,
        )

        ancho = min(
            vista.ancho,
            max(
                1120,
                self.width() - 32,
            ),
        )

        alto = min(
            vista.alto,
            max(
                720,
                self.height() - 32,
            ),
        )

        ventana.resize(
            ancho,
            alto,
        )

        layout = QVBoxLayout(
            ventana,
        )

        layout.setContentsMargins(
            6,
            6,
            6,
            6,
        )

        layout.addWidget(
            vista,
        )

        def abrir_edicion():

            self._mostrar_dialogo_formulario(
                id_registro=id_registro,
            )

            vista.recargar()

            self.cargar_datos()

        vista.editar_solicitado.connect(
            abrir_edicion,
        )

        vista.actualizado.connect(
            self.cargar_datos,
        )

        vista.cerrar.connect(
            ventana.accept,
        )

        ventana.exec()

        vista.deleteLater()

    def _ventana_padre_vista(
        self,
    ):

        return self

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        return (
            f"{self.titulo_singular} "
            f"#{id_registro}"
        )
