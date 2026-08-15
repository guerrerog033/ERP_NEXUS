from PySide6.QtWidgets import (
    QMessageBox,
)

from aplicacion.framework.base.page import Page
from aplicacion.framework.datagrid.datagrid import DataGrid


class MaestroBase(Page):

    titulo = "Maestro"

    def __init__(self):

        super().__init__()

        self.crear_interfaz()

    def crear_interfaz(self):

        self.grid = DataGrid()

        self.agregar_widget(
            self.grid,
            stretch=1,
        )

        self.toolbar = self.grid.toolbar

        self.tabla = self.grid.tabla

        self.txt_buscar = self.grid.txt_buscar

        self.btn_nuevo = self.grid.btn_nuevo

        self.btn_editar = self.grid.btn_editar

        self.btn_consultar = self.grid.btn_consultar

        self.btn_eliminar = self.grid.btn_eliminar

        self.btn_actualizar = self.grid.btn_actualizar

        self.btn_excel = self.grid.btn_excel

        self.btn_pdf = self.grid.btn_pdf

        self.btn_imprimir = self.grid.btn_imprimir

        self.lbl_total = self.grid.lbl_total

    def actualizar_total(self):

        self.grid.actualizar_total(
            self.tabla.rowCount(),
        )

    def obtener_id_seleccionado(self):

        if hasattr(
            self,
            "table_binding",
        ) and self.table_binding is not None:

            registro = (
                self.table_binding.seleccionado()
            )

            if registro is not None:

                return getattr(
                    registro,
                    "id",
                    None,
                )

        fila = self.tabla.currentRow()

        if fila < 0:

            return None

        item = self.tabla.item(
            fila,
            0,
        )

        if item is None:

            return None

        try:

            return int(
                item.text()
            )

        except ValueError:

            return None

    def mostrar_error(
        self,
        mensaje,
    ):

        QMessageBox.critical(
            self,
            "Error",
            mensaje,
        )

    def mostrar_info(
        self,
        mensaje,
    ):

        QMessageBox.information(
            self,
            "Información",
            mensaje,
        )

    def confirmar(
        self,
        mensaje,
    ):

        return (
            QMessageBox.question(
                self,
                "Confirmar",
                mensaje,
                QMessageBox.Yes
                | QMessageBox.No,
            )
            == QMessageBox.Yes
        )
