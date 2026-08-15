from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorPlanCuenta


class PlanCuentaDataSource(SqlAlchemyDataSource):

    controlador = ControladorPlanCuenta
