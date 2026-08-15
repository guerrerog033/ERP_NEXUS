from aplicacion.framework.crud.crud_documento import CrudDocumento
from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.modulos.ventas.facturas.datasource import (
    FacturaVentaDataSource,
)
from aplicacion.modulos.ventas.facturas.factura_definition import (
    FacturaVentaDefinition,
)
from aplicacion.modulos.ventas.facturas.formulario import (
    FormularioFacturaVenta,
)
from aplicacion.modulos.ventas.facturas.vista_factura import (
    VistaFacturaVenta,
)


class FormularioFacturaLista:

    definition = FacturaVentaDefinition


class MaestroFacturasVenta(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Facturas de venta"

    titulo_singular = "Factura de venta"

    datasource = FacturaVentaDataSource

    formulario = FormularioFacturaLista

    vista_documento = VistaFacturaVenta

    def crear_formulario(
        self,
        id_registro=None,
        parent=None,
        *,
        modo=None,
    ):

        kwargs = {
            "id_registro": id_registro,
        }

        if parent is not None:

            kwargs["parent"] = parent

        return FormularioFacturaVenta(
            **kwargs,
        )

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        factura = self.datasource.obtener_completa(
            id_registro,
        )

        if factura is None:

            return "Factura de venta"

        return f"Factura {factura.numero}"

    def _titulo_dialogo_formulario(
        self,
        id_registro=None,
    ) -> str:

        if id_registro is not None:

            return "Editar Factura"

        return "Nueva Factura"

    def _tamanio_dialogo_formulario(
        self,
        formulario,
    ) -> tuple[int, int]:

        margen = self._margen_dialogo_formulario()

        ancho = min(
            formulario.ancho,
            max(
                1100,
                self.width() - margen,
            ),
        )

        alto = min(
            formulario.alto,
            max(
                620,
                self.height() - margen,
            ),
        )

        return ancho, alto
