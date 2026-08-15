from __future__ import annotations

from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionGuiaRemisionElectronica
from .servicios import ServicioGuiaRemisionElectronica


class ControladorGuiaRemisionElectronica(ControladorBase):

    servicio = ServicioGuiaRemisionElectronica

    @classmethod
    def emitir_electronica(
        cls,
        id_registro: int,
    ):

        return IntegracionGuiaRemisionElectronica.emitir_electronica(
            id_registro,
        )

    @classmethod
    def crear_desde_remision(
        cls,
        remision_id: int,
        **kwargs,
    ):

        return cls.servicio.crear_desde_remision(
            remision_id,
            **kwargs,
        )
