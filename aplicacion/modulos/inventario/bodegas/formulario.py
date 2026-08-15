from aplicacion.framework.base.formulario_base import FormularioBase

from .bodega_definition import BodegaDefinition
from .datasource import BodegaDataSource


class FormularioBodega(FormularioBase):

    titulo = "Bodegas"

    definition = BodegaDefinition

    datasource = BodegaDataSource
