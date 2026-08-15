from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionComprobanteEgreso
from .servicios import ServicioComprobanteEgreso


class ControladorComprobanteEgreso(ControladorBase):

    servicio = ServicioComprobanteEgreso

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
        proveedor_id: int,
    ):

        return cls.servicio.listar_facturas_pendientes(
            proveedor_id,
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

        return IntegracionComprobanteEgreso.contabilizar(
            id_registro,
        )
