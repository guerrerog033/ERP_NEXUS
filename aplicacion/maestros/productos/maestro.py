from PySide6.QtWidgets import QFileDialog, QMessageBox

from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.maestros.productos.datasource import (
    ProductoDataSource,
)
from aplicacion.maestros.productos.formulario import (
    FormularioProducto,
)


class MaestroProductos(CrudMaster):

    titulo = "Productos"

    titulo_singular = "Producto"

    datasource = ProductoDataSource

    formulario = FormularioProducto

    def crear_interfaz(self):

        super().crear_interfaz()

        menu = self.toolbar.btn_mas.menu()

        menu.addSeparator()

        accion_plantilla = menu.addAction(
            "Descargar plantilla de importación",
        )

        accion_plantilla.triggered.connect(
            self._descargar_plantilla_productos,
        )

        accion_importar = menu.addAction(
            "Importar productos desde Excel",
        )

        accion_importar.triggered.connect(
            self._importar_productos_excel,
        )

    def _descargar_plantilla_productos(self):

        from aplicacion.maestros.productos.importacion_excel import (
            generar_plantilla,
        )

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar plantilla de importación",
            "plantilla_productos.xlsx",
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

    def _importar_productos_excel(self):

        from aplicacion.maestros.productos.importacion_excel import (
            importar_desde_excel,
        )

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Importar productos desde Excel",
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
            "Importación de productos",
            mensaje,
        )

        self.cargar_datos()

    def _tamanio_dialogo_formulario(
        self,
        formulario,
    ) -> tuple[int, int]:

        margen = self._margen_dialogo_formulario()

        ancho = min(
            formulario.ancho,
            max(
                720,
                self.width() - margen,
            ),
        )

        alto = min(
            formulario.alto,
            max(
                600,
                self.height() - margen,
            ),
        )

        return ancho, alto

    def _limites_dialogo_formulario(
        self,
        ancho: int,
        alto: int,
    ) -> tuple[
        tuple[int, int],
        tuple[int, int] | None,
    ]:

        return (
            (
                min(
                    ancho,
                    720,
                ),
                min(
                    alto,
                    600,
                ),
            ),
            None,
        )
