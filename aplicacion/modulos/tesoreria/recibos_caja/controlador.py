from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionReciboCaja
from .servicios import ServicioReciboCaja


class ControladorReciboCaja(ControladorBase):

    servicio = ServicioReciboCaja

    @classmethod
    def obtener_completo(
        cls,
        id_registro,
    ):

        return cls.servicio.obtener_completo(
            id_registro,
        )

    @classmethod
    def listar_facturas_pendientes(
        cls,
        cliente_id: int,
    ):

        return cls.servicio.listar_facturas_pendientes(
            cliente_id,
        )

    @classmethod
    def guardar_completo(
        cls,
        cabecera,
        lineas,
        *,
        id_registro=None,
    ):

        return cls.servicio.guardar_completo(
            cabecera,
            lineas,
            id_registro=id_registro,
        )

    @classmethod
    def contabilizar(
        cls,
        id_registro,
    ):

        return IntegracionReciboCaja.contabilizar(
            id_registro,
        )
