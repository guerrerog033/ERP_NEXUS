from aplicacion.comunes.controlador_base import ControladorBase

from aplicacion.modulos.nomina.servicios import (
    ServicioEmpleado,
)


class ControladorEmpleado(ControladorBase):

    servicio = ServicioEmpleado
