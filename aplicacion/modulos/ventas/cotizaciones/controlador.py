from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionCotizacion
from .servicios import ServicioCotizacion


class ControladorCotizacion(ControladorBase):

    servicio = ServicioCotizacion

    @classmethod
    def confirmar_cotizacion(
        cls,
        id_registro: int,
    ):

        return IntegracionCotizacion.confirmar_cotizacion(
            id_registro,
        )

    @classmethod
    def guardar_completa(        cls,
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
    def obtener_completa(
        cls,
        id_registro,
    ):

        return cls.servicio.obtener_completa(
            id_registro,
        )
