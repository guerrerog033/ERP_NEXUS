from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorRol


class RolDataSource(SqlAlchemyDataSource):

    controlador = ControladorRol
