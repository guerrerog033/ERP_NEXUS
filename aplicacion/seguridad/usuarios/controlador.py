from aplicacion.comunes.controlador_base import ControladorBase

from .servicios import ServicioUsuario


class ControladorUsuario(ControladorBase):

    servicio = ServicioUsuario
