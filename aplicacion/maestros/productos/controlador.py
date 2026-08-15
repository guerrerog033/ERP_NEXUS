from aplicacion.comunes.controlador_base import ControladorBase

from .servicios import ServicioProducto


class ControladorProducto(ControladorBase):

    servicio = ServicioProducto

    @classmethod
    def guardar_completo(
        cls,
        datos,
        id_registro=None,
    ):

        return cls.servicio.guardar_completo(
            datos,
            id_registro,
        )

    @classmethod
    def obtener_completo(
        cls,
        id_registro,
    ):

        return cls.servicio.obtener_completo(
            id_registro,
        )
