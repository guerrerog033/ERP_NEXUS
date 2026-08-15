from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)

from .datasource import OportunidadDataSource
from .oportunidad_definition import OportunidadDefinition


class FormularioOportunidad(FormularioBase):

    titulo = "Oportunidades"

    definition = OportunidadDefinition

    datasource = OportunidadDataSource
