from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)

from .datasource import NovedadDataSource
from .novedad_definition import NovedadDefinition


class FormularioNovedad(FormularioBase):

    titulo = "Novedades"

    definition = NovedadDefinition

    datasource = NovedadDataSource
