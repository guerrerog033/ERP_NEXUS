from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import EmpresaControlador


class EmpresaDataSource(SqlAlchemyDataSource):

    controlador = EmpresaControlador