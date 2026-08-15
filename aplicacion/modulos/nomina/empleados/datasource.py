from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorEmpleado


class EmpleadoDataSource(SqlAlchemyDataSource):

    controlador = ControladorEmpleado
