from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionFacturaVenta
from .servicios import ServicioFacturaVenta


class ControladorFacturaVenta(ControladorBase):

    servicio = ServicioFacturaVenta

    @classmethod
    def obtener_completa(
        cls,
        id_registro,
    ):

        return cls.servicio.obtener_completa(
            id_registro,
        )

    @classmethod
    def confirmar_venta(
        cls,
        id_registro,
        *,
        emitir_dian: bool = False,
    ):

        return IntegracionFacturaVenta.confirmar_venta(
            id_registro,
            emitir_dian=emitir_dian,
        )

    @classmethod
    def emitir_electronica(
        cls,
        id_registro,
    ):

        return IntegracionFacturaVenta.emitir_electronica(
            id_registro,
        )

    @classmethod
    def contabilizar(
        cls,
        id_registro,
    ):

        return IntegracionFacturaVenta.contabilizar(
            id_registro,
        )

    @classmethod
    def actualizar_formato_impresion(
        cls,
        id_registro,
        formato: str,
    ):

        return cls.servicio.actualizar_formato_impresion(
            id_registro,
            formato,
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
