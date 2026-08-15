from aplicacion.comunes.controlador_base import ControladorBase

from .servicios import ServicioPlanCuenta


class ControladorPlanCuenta(ControladorBase):

    servicio = ServicioPlanCuenta
