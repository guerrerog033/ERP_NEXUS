from PySide6.QtCore import QObject, Qt, QThread





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

        self._registrar_atajos_lista()

    def _registrar_atajos_lista(
        self,
    ) -> None:

        from aplicacion.framework.ui.atajos import (
            pulsar,
            registrar_atajos,
        )

        def enfocar_buscador():

            if self.txt_buscar is not None:

                self.txt_buscar.setFocus()

                self.txt_buscar.selectAll()

        registrar_atajos(
            self,
            (
                (("Ctrl+N", "Insert"), lambda: pulsar(self.btn_nuevo)),
                ("F2", lambda: pulsar(self.btn_editar)),
                ("Delete", lambda: pulsar(self.btn_eliminar)),
                (("Ctrl+F", "F3"), enfocar_buscador),
                ("F5", self.actualizar),
                ("Ctrl+P", self._imprimir_desde_tecla),
                ("Ctrl+E", self._excel_desde_tecla),
                ("Home", lambda: self._navegar_lista("primero")),
                ("End", lambda: self._navegar_lista("ultimo")),
            ),
        )

        if self.table_engine is not None:

            # Enter sobre la tabla abre el registro seleccionado.
            registrar_atajos(
                self.table_engine.widget,
                (
                    (("Return", "Enter"), lambda: pulsar(self.btn_editar)),
                ),
                contexto=Qt.ShortcutContext.WidgetShortcut,
            )

        for boton, texto in (
            (self.btn_nuevo, "Nuevo (Ctrl+N)"),
            (self.btn_editar, "Editar (F2 o Enter)"),
            (self.btn_eliminar, "Eliminar (Supr)"),
        ):

            if boton is not None:

                boton.setToolTip(
                    texto,
                )



    def _imprimir_desde_tecla(
        self,
    ) -> None:

        accion = getattr(
            self,
            "btn_imprimir",
            None,
        )

        if accion is not None and hasattr(
            accion,
            "trigger",
        ):

            accion.trigger()

    def _excel_desde_tecla(
        self,
    ) -> None:

        accion = getattr(
            self,
            "btn_excel",
            None,
        )

        if accion is not None and hasattr(
            accion,
            "trigger",
        ):

            accion.trigger()

    def _navegar_lista(
        self,
        destino: str,
    ) -> None:

        grid = getattr(
            self,
            "grid",
            None,
        )

        if grid is not None and hasattr(
            grid,
            "navegar",
        ):

            grid.navegar(
                destino,
            )

    def teclas_contexto(
        self,
    ) -> list:
        """Teclas que muestra la barra inferior para esta lista."""

        from aplicacion.framework.ui.atajos import pulsar

        def enfocar_buscador():

            if self.txt_buscar is not None:

                self.txt_buscar.setFocus()

                self.txt_buscar.selectAll()

        teclas = [
            ("Ctrl+N", "Nuevo", lambda: pulsar(self.btn_nuevo)),
            ("F2", "Editar", lambda: pulsar(self.btn_editar)),
        ]

        teclas += [
            ("Supr", "Eliminar", lambda: pulsar(self.btn_eliminar)),
            ("F3", "Buscar", enfocar_buscador),
            ("F5", "Actualizar", self.actualizar),
            ("Ctrl+P", "Imprimir", self._imprimir_desde_tecla),
            ("Ctrl+E", "Excel", self._excel_desde_tecla),
        ]

        return teclas

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


