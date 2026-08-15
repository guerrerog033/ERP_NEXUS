from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorProducto


class ProductoDataSource(SqlAlchemyDataSource):

    controlador = ControladorProducto

    def guardar(
        self,
        datos,
        id_registro=None,
    ):

        return self.controlador.guardar_completo(
            datos,
            id_registro,
        )

    def obtener_completo(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completo(
            id_registro,
        )
