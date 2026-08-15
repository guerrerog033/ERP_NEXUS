from aplicacion.framework.form import FormDefinition

from .cotizaciones_table import (
    CotizacionTable,
)


class CotizacionDefinition(FormDefinition):

    titulo = "Cotizaciones"

    campos = ()

    table_definition = CotizacionTable
