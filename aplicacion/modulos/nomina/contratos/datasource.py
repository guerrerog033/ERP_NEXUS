from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorContrato


class ContratoDataSource(SqlAlchemyDataSource):

    controlador = ControladorContrato
