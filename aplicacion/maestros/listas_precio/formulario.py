from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)

from .datasource import ListaPrecioDataSource
from .lista_precio_definition import ListaPrecioDefinition


class FormularioListaPrecio(FormularioBase):

    titulo = "Listas de precio"

    definition = ListaPrecioDefinition

    datasource = ListaPrecioDataSource
