from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)

from .datasource import ImpuestoDataSource
from .impuesto_definition import ImpuestoDefinition


class FormularioImpuesto(FormularioBase):

    titulo = "Impuestos"

    definition = ImpuestoDefinition

    datasource = ImpuestoDataSource
