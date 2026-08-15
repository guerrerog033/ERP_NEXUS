from aplicacion.comunes.controlador_base import ControladorBase

from aplicacion.modulos.nomina.servicios import (
    ServicioContrato,
)


class ControladorContrato(ControladorBase):

    servicio = ServicioContrato
