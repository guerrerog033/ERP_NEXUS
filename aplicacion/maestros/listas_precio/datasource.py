from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorListaPrecio


class ListaPrecioDataSource(SqlAlchemyDataSource):

    controlador = ControladorListaPrecio
