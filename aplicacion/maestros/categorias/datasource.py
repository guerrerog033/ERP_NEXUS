from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorCategoria


class CategoriaDataSource(SqlAlchemyDataSource):

    controlador = ControladorCategoria