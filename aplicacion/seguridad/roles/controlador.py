from aplicacion.comunes.controlador_base import ControladorBase

from .servicios import ServicioRol


class ControladorRol(ControladorBase):

    servicio = ServicioRol
