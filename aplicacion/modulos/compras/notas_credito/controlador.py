from __future__ import annotations

from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionNotaCreditoCompra
from .servicios import ServicioNotaCreditoCompra


class ControladorNotaCreditoCompra(ControladorBase):

    servicio = ServicioNotaCreditoCompra

    @classmethod
    def aplicar(
        cls,
        id_registro: int,
    ):

        return IntegracionNotaCreditoCompra.aplicar(
            id_registro,
        )

    @classmethod
    def contabilizar(
        cls,
        id_registro: int,
    ):

        return IntegracionNotaCreditoCompra.contabilizar(
            id_registro,
        )
