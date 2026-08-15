from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorBodega


class BodegaDataSource(SqlAlchemyDataSource):

    controlador = ControladorBodega
