from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorActividad


class ActividadDataSource(SqlAlchemyDataSource):

    controlador = ControladorActividad
