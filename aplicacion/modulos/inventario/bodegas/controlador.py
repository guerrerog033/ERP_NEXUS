from aplicacion.comunes.controlador_base import ControladorBase

from .servicios import ServicioBodega


class ControladorBodega(ControladorBase):

    servicio = ServicioBodega
