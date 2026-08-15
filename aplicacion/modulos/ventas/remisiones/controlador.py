from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionRemision
from .servicios import ServicioRemision


class ControladorRemision(ControladorBase):

    servicio = ServicioRemision

    @classmethod
    def confirmar_remision(
        cls,
        id_registro: int,
    ):

        return IntegracionRemision.confirmar_remision(
            id_registro,
        )

    @classmethod
    def obtener_completa(
        cls,
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
    def despachar(
        cls,
        id_registro,
    ):

        return cls.servicio.despachar(
            id_registro,
        )
