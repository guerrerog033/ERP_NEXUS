from PySide6.QtCore import QObject, QThread


class CrudEventos(QObject):
    """
    Responsable de conectar los eventos del CRUD.
    """

    def conectar_eventos(self):

        self.btn_nuevo.clicked.connect(
            self.nuevo,
        )

        self.btn_editar.clicked.connect(
            self.editar,
        )

        btn_consultar = getattr(
            self,
            "btn_consultar",
            None,
        )

        if btn_consultar is not None:

            btn_consultar.clicked.connect(
                self.consultar,
            )

        self.btn_eliminar.clicked.connect(
            self.eliminar,
        )

        toolbar = getattr(
            self.grid,
            "toolbar",
            None,
        )

        if toolbar is not None:

            toolbar.actualizar.connect(
                self.actualizar,
            )

            toolbar.excel.connect(
                self.exportar_excel,
            )

            toolbar.pdf.connect(
                self.exportar_pdf,
            )

            toolbar.imprimir.connect(
                self.imprimir_listado,
            )

        elif getattr(
            self,
            "btn_actualizar",
            None,
        ) is not None:

            if hasattr(
                self.btn_actualizar,
                "triggered",
            ):
                self.btn_actualizar.triggered.connect(
                    self.actualizar,
                )
            else:
                self.btn_actualizar.clicked.connect(
                    self.actualizar,
                )

        if self.txt_buscar is not None:

            self.txt_buscar.textChanged.connect(
                self.buscar,
            )

        if self.table_engine is not None:

            self.table_engine.widget.doubleClicked.connect(
                self.editar,
            )

    def imprimir_listado(
        self,
    ) -> None:

        if hasattr(
            self,
            "mostrar_info",
        ):
            self.mostrar_info(
                "Impresión del listado disponible próximamente.",
            )

    def consultar(
        self,
    ) -> None:

        id_registro = (
            self.obtener_id_seleccionado()
        )

        if id_registro is None:

            self.mostrar_error(
                "Seleccione un registro.",
            )

            return

        from aplicacion.framework.form.modo import (
            ModoFormulario,
        )

        if self.usar_formulario_modal():

            self._mostrar_dialogo_formulario(
                id_registro=id_registro,
                modo=ModoFormulario.CONSULTA,
            )

            return

        formulario = self.crear_formulario(
            id_registro=id_registro,
            modo=ModoFormulario.CONSULTA,
        )

        self.abrir_formulario(
            formulario,
            f"Consultar {self.titulo}",
        )
