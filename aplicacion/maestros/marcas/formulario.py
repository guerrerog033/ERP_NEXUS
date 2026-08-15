from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)

from aplicacion.maestros.marcas.datasource import (
    MarcaDataSource,
)

from aplicacion.maestros.marcas.marca_definition import (
    MarcaDefinition,
)


class FormularioMarca(FormularioBase):

    titulo = "Marcas"

    definition = MarcaDefinition

    datasource = MarcaDataSource