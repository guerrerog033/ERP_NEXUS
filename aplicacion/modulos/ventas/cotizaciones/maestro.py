from aplicacion.framework.crud.crud_documento import CrudDocumento
from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.modulos.ventas.cotizaciones.datasource import (
    CotizacionDataSource,
)

from aplicacion.modulos.ventas.cotizaciones.formulario import (
    FormularioCotizacion,
)

from aplicacion.modulos.ventas.cotizaciones.vista_cotizacion import (
    VistaCotizacion,
)


class MaestroCotizaciones(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Cotizaciones"

    titulo_singular = "Cotización"

    datasource = CotizacionDataSource

    formulario = FormularioCotizacion

    vista_documento = VistaCotizacion

    def __init__(self):

        from aplicacion.base_datos.migraciones import (
            migrar_cotizaciones,
            migrar_productos,
        )

        from aplicacion.maestros.impuestos.servicios import (
            ServicioImpuesto,
        )

        migrar_productos()
        migrar_cotizaciones()
        ServicioImpuesto.inicializar_predeterminados()

        super().__init__()

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        cotizacion = self.datasource.obtener_completa(
            id_registro,
        )

        if cotizacion is None:

            return "Cotización"

        return f"Cotización {cotizacion.numero}"

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
                520,
                self.height() - margen,
            ),
        )

        return ancho, alto

    def _titulo_dialogo_formulario(
        self,
        id_registro=None,
    ) -> str:

        if id_registro is not None:

            return "Editar Cotización"

        return "Nueva Cotización"
