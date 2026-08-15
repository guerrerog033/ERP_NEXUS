from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorNovedad


class NovedadDataSource(SqlAlchemyDataSource):

    controlador = ControladorNovedad
