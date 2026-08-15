from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)

from .contrato_definition import ContratoDefinition
from .datasource import ContratoDataSource


class FormularioContrato(FormularioBase):

    titulo = "Contratos"

    definition = ContratoDefinition

    datasource = ContratoDataSource
