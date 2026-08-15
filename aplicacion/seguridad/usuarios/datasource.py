from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorUsuario


class UsuarioDataSource(SqlAlchemyDataSource):

    controlador = ControladorUsuario
