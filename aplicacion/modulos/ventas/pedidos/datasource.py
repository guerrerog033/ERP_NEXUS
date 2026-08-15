from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorPedido


class PedidoDataSource(SqlAlchemyDataSource):

    controlador = ControladorPedido

    def confirmar_pedido(
        self,
        id_registro: int,
    ):

        return self.controlador.confirmar_pedido(
            id_registro,
        )

    def obtener_completa(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completa(
            id_registro,
        )

    def guardar_completa(
        self,
        cabecera,
        lineas,
        id_registro=None,
    ):

        return self.controlador.guardar_completa(
            cabecera,
            lineas,
            id_registro,
        )

    def reservar_inventario(
        self,
        id_registro: int,
        *,
        bodega_id: int | None = None,
    ):

        return self.controlador.reservar_inventario(
            id_registro,
            bodega_id=bodega_id,
        )

    def liberar_reserva(
        self,
        id_registro: int,
    ):

        return self.controlador.liberar_reserva(
            id_registro,
        )
