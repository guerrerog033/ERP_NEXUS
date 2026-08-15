from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorUnidadMedida


class UnidadMedidaDataSource(SqlAlchemyDataSource):

    controlador = ControladorUnidadMedida
