from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)

from .actividad_definition import ActividadDefinition
from .datasource import ActividadDataSource


class FormularioActividad(FormularioBase):

    titulo = "Actividades"

    definition = ActividadDefinition

    datasource = ActividadDataSource
