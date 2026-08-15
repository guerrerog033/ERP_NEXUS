from aplicacion.comunes.controlador_base import ControladorBase

from .integracion import IntegracionNotaDebitoVenta
from .servicios import ServicioNotaDebitoVenta


class ControladorNotaDebitoVenta(ControladorBase):

    servicio = ServicioNotaDebitoVenta

    @classmethod
    def obtener_completa(
        cls,
        id_registro,
    ):

        return cls.servicio.obtener_completa(
            id_registro,
        )

    @classmethod
    def confirmar_generacion(
        cls,
        id_registro,
        *,
        emitir_dian: bool = False,
    ):

        return IntegracionNotaDebitoVenta.confirmar_generacion(
            id_registro,
            emitir_dian=emitir_dian,
        )

    @classmethod
    def emitir_electronica(
        cls,
        id_registro,
    ):

        return IntegracionNotaDebitoVenta.emitir_electronica(
            id_registro,
        )

    @classmethod
    def contabilizar(
        cls,
        id_registro,
    ):

        return IntegracionNotaDebitoVenta.contabilizar(
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

    @classmethod
    def crear_desde_factura(
        cls,
        factura_id: int,
        motivo: str | None = None,
    ):

        return cls.servicio.crear_desde_factura(
            factura_id,
            motivo,
        )
