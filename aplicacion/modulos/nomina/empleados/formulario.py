from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)

from .datasource import EmpleadoDataSource
from .empleado_definition import EmpleadoDefinition


class FormularioEmpleado(FormularioBase):

    titulo = "Empleados"

    definition = EmpleadoDefinition

    datasource = EmpleadoDataSource
