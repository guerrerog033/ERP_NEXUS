from aplicacion.comunes.controlador_base import ControladorBase

from .servicios import ServicioListaPrecio


class ControladorListaPrecio(ControladorBase):

    servicio = ServicioListaPrecio
