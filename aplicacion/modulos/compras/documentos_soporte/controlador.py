from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionDocumentoSoporte
from .servicios import ServicioDocumentoSoporte


class ControladorDocumentoSoporte(ControladorBase):

    servicio = ServicioDocumentoSoporte

    @classmethod
    def obtener_completa(
        cls,
        id_registro,
    ):

        return cls.servicio.obtener_completa(
            id_registro,
        )

    @classmethod
    def emitir_electronica(
        cls,
        id_registro,
    ):

        return IntegracionDocumentoSoporte.emitir_electronica(
            id_registro,
        )

    @classmethod
    def guardar_completa(
        cls,
        cabecera,
        lineas,
        id_registro=None,
    ):

        return cls.servicio.guardar_completa(
            cabecera,
            lineas,
            id_registro,
        )
