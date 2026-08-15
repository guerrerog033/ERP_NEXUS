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
