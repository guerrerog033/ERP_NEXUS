from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionPedido
from .servicios import ServicioPedido


class ControladorPedido(ControladorBase):

    servicio = ServicioPedido

    @classmethod
    def confirmar_pedido(
        cls,
        id_registro: int,
    ):

        return IntegracionPedido.confirmar_pedido(
            id_registro,
        )

    @classmethod
    def obtener_completa(        cls,
        id_registro,
    ):

        return cls.servicio.obtener_completa(
            id_registro,
        )

    @classmethod
    def guardar_completa(
        cls,
        cabecera,
        lineas,
        id_registro=None,
    ):

        return cls.servicio.guardar_completa(
            cabecera,
            lineas,
            id_registro,
        )

    @classmethod
    def reservar_inventario(
        cls,
        id_registro: int,
        *,
        bodega_id: int | None = None,
    ):

        return cls.servicio.reservar_inventario(
            id_registro,
            bodega_id=bodega_id,
        )

    @classmethod
    def liberar_reserva(
        cls,
        id_registro: int,
    ):

        return cls.servicio.liberar_reserva(
            id_registro,
        )
