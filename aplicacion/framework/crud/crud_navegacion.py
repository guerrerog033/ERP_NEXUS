from PySide6.QtCore import Qt

from PySide6.QtWidgets import QMessageBox

from aplicacion.framework.app_context import AppContext


class CrudNavegacion:
    """
    Responsable de la navegación entre
    maestros y formularios.
    """

    # ==================================================
    # Abrir formulario
    # ==================================================

    def abrir_formulario(
        self,
        formulario,
        titulo,
    ):

        area_trabajo = AppContext.area_trabajo

        if area_trabajo is None:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No hay área de trabajo disponible. "
                    "Reinicie la aplicación."
                ),
            )

            formulario.deleteLater()

            return

        if formulario.parent() is None:

            formulario.setParent(
                area_trabajo,
            )

        formulario.setAttribute(
            Qt.WA_DontShowOnScreen,
            True,
        )

        formulario.hide()

        formulario.guardado.connect(
            self.cargar_datos
        )

        formulario.cerrar.connect(

            lambda: area_trabajo.cerrar_widget(
                formulario
            )

        )

        area_trabajo.abrir(
            formulario,
            titulo,
        )

    # ==================================================
    # Nuevo
    # ==================================================

    def nuevo(self):

        formulario = self.crear_formulario()

        self.abrir_formulario(
            formulario,
            f"Nuevo {self.titulo}",
        )

    # ==================================================
    # Editar
    # ==================================================

    def editar(self):

        id_registro = (
            self.obtener_id_seleccionado()
        )

        if id_registro is None:

            self.mostrar_error(
                "Seleccione un registro."
            )

            return

        formulario = self.crear_formulario(
            id_registro=id_registro,
        )

        self.abrir_formulario(
            formulario,
            f"Editar {self.titulo}",
        )
