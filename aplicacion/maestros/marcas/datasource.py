from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorMarca


class MarcaDataSource(SqlAlchemyDataSource):

    controlador = ControladorMarca