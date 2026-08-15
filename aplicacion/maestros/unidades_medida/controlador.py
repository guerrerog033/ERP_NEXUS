from aplicacion.comunes.controlador_base import ControladorBase

from .servicios import ServicioUnidadMedida


class ControladorUnidadMedida(ControladorBase):

    servicio = ServicioUnidadMedida
