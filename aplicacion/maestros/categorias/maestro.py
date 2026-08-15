from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.maestros.categorias.datasource import (
    CategoriaDataSource,
)

from aplicacion.maestros.categorias.formulario import (
    FormularioCategoria,
)


class MaestroCategorias(CrudMaster):

    titulo = "Categorías"

    titulo_singular = "Categoría"

    datasource = CategoriaDataSource

    formulario = FormularioCategoria