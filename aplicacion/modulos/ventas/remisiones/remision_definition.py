from aplicacion.framework.form import FormDefinition

from .remisiones_table import (
    RemisionTable,
)


class RemisionDefinition(FormDefinition):

    titulo = "Remisiones internas"

    campos = ()

    table_definition = RemisionTable
