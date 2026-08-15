from aplicacion.comunes.controlador_base import ControladorBase

from aplicacion.modulos.crm.servicios import (
    ServicioActividadCRM,
)


class ControladorActividad(ControladorBase):

    servicio = ServicioActividadCRM
