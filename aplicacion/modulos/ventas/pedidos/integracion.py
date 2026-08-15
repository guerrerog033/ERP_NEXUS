from __future__ import annotations

from .repositorio import RepositorioPedido
from .servicios import ServicioPedido


class IntegracionPedido:

    @classmethod
    def confirmar_pedido(
        cls,
        id_registro: int,
    ):

        pedido = ServicioPedido.obtener_completa(
            id_registro,
        )

        if pedido is None:

            raise ValueError(
                "No se encontró el pedido.",
            )

        if pedido.estado != "borrador":

            raise ValueError(
                "El pedido ya fue confirmado.",
            )

        RepositorioPedido.actualizar_estado_confirmacion(
            id_registro,
            estado="pendiente",
        )

        return ServicioPedido.obtener_completa(
            id_registro,
        )
