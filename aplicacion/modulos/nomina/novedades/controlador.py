from aplicacion.comunes.controlador_base import ControladorBase

from aplicacion.modulos.nomina.servicios import (
    ServicioNovedad,
)


class ControladorNovedad(ControladorBase):

    servicio = ServicioNovedad
