from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorOportunidad


class OportunidadDataSource(SqlAlchemyDataSource):

    controlador = ControladorOportunidad
