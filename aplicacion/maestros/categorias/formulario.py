from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)

from aplicacion.maestros.categorias.datasource import (
    CategoriaDataSource,
)

from aplicacion.maestros.categorias.categoria_definition import (
    CategoriaDefinition,
)


class FormularioCategoria(FormularioBase):

    titulo = "Categorías"

    definition = CategoriaDefinition

    datasource = CategoriaDataSource