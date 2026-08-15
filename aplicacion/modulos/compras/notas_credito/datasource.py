from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorNotaCreditoCompra


class NotaCreditoCompraDataSource(SqlAlchemyDataSource):

    controlador = ControladorNotaCreditoCompra

    def obtener_completa(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completa(
            id_registro,
        )

    def aplicar(
        self,
        id_registro,
    ):

        return self.controlador.aplicar(
            id_registro,
        )

    def contabilizar(
        self,
        id_registro,
    ):

        return self.controlador.contabilizar(
            id_registro,
        )
