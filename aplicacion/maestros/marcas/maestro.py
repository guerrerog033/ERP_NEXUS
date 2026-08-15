from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.maestros.marcas.datasource import (
    MarcaDataSource,
)

from aplicacion.maestros.marcas.formulario import (
    FormularioMarca,
)


class MaestroMarcas(CrudMaster):

    titulo = "Marcas"

    titulo_singular = "Marca"

    datasource = MarcaDataSource

    formulario = FormularioMarca