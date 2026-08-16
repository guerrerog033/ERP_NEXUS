from PySide6.QtWidgets import QFileDialog, QMessageBox

from aplicacion.framework.crud.crud_master import CrudMaster



from .controlador import TerceroControlador

from .datasource import (

    ClienteDataSource,

    OtroDataSource,

    ProveedorDataSource,

    TerceroDataSource,

)

from .formulario import TerceroFormulario
from .formulario_cliente import (
    ClienteFormulario,
)





class MaestroTerceros(CrudMaster):



    titulo = "Terceros"



    titulo_singular = "Tercero"



    controlador = TerceroControlador



    datasource = TerceroDataSource



    formulario = TerceroFormulario



    tipo_filtro = None



    def crear_interfaz(self):

        super().crear_interfaz()

        menu = self.toolbar.btn_mas.menu()

        menu.addSeparator()

        accion_plantilla = menu.addAction(
            "Descargar plantilla de importación",
        )

        accion_plantilla.triggered.connect(
            self._descargar_plantilla_terceros,
        )

        accion_importar = menu.addAction(
            "Importar terceros desde Excel",
        )

        accion_importar.triggered.connect(
            self._importar_terceros_excel,
        )

    def _descargar_plantilla_terceros(self):

        from aplicacion.maestros.terceros.importacion_excel import (
            generar_plantilla,
        )

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar plantilla de importación",
            "plantilla_terceros.xlsx",
            "Excel (*.xlsx)",
        )

        if not ruta:

            return

        try:

            generar_plantilla(ruta)

        except OSError as error:

            self.mostrar_error(
                f"No se pudo generar la plantilla: {error}",
            )

            return

        self.mostrar_info(
            f"Plantilla guardada en:\n{ruta}",
        )

    def _importar_terceros_excel(self):

        from aplicacion.maestros.terceros.importacion_excel import (
            importar_desde_excel,
        )

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Importar terceros desde Excel",
            "",
            "Excel (*.xlsx)",
        )

        if not ruta:

            return

        try:

            resultado = importar_desde_excel(ruta)

        except Exception as error:  # noqa: BLE001

            self.mostrar_error(
                f"No se pudo leer el archivo: {error}",
            )

            return

        mensaje = (
            f"Creados: {resultado.creados}\n"
            f"Actualizados: {resultado.actualizados}\n"
            f"Con error: {len(resultado.errores)}"
        )

        if resultado.errores:

            detalle = "\n".join(
                f"Fila {fila}: {error}"
                for fila, error in resultado.errores[:15]
            )

            if len(resultado.errores) > 15:

                detalle += (
                    f"\n… y {len(resultado.errores) - 15} más."
                )

            mensaje = f"{mensaje}\n\n{detalle}"

        QMessageBox.information(
            self,
            "Importación de terceros",
            mensaje,
        )

        self.cargar_datos()

    def crear_formulario(

        self,

        id_registro=None,

        parent=None,

        *,

        modo=None,

    ):

        kwargs = {

            "id_registro": id_registro,

            "tipo_tercero_inicial": self.tipo_filtro,

            "parent": parent,

        }

        if modo is not None:

            kwargs["modo"] = modo

        return self.formulario(

            **kwargs,

        )



    def _icono_dialogo_formulario(self):



        from aplicacion.recursos.ui.recursos import (

            Recursos,

        )



        return Recursos.icono_terceros()



    def _limites_dialogo_formulario(

        self,

        ancho: int,

        alto: int,

    ) -> tuple[

        tuple[int, int],

        tuple[int, int] | None,

    ]:



        minimo, _ = super()._limites_dialogo_formulario(

            ancho,

            alto,

        )



        return (

            minimo,

            (

                max(

                    640,

                    self.width() - 16,

                ),

                max(

                    480,

                    self.height() - 16,

                ),

            ),

        )





class MaestroClientes(MaestroTerceros):



    titulo = "Clientes"



    titulo_singular = "Cliente"



    tipo_filtro = "Cliente"



    datasource = ClienteDataSource

    formulario = ClienteFormulario





class MaestroProveedores(MaestroTerceros):



    titulo = "Proveedores"



    titulo_singular = "Proveedor"



    tipo_filtro = "Proveedor"



    datasource = ProveedorDataSource





class MaestroOtros(MaestroTerceros):



    titulo = "Otros"



    titulo_singular = "Tercero"



    tipo_filtro = "Otro"



    datasource = OtroDataSource

