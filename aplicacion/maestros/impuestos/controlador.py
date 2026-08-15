from aplicacion.comunes.controlador_base import ControladorBase

from .servicios import ServicioImpuesto


class ControladorImpuesto(ControladorBase):

    servicio = ServicioImpuesto
