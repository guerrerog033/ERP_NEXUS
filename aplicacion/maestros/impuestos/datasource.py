from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorImpuesto


class ImpuestoDataSource(SqlAlchemyDataSource):

    controlador = ControladorImpuesto
