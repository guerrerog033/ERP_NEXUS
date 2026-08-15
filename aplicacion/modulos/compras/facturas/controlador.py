from aplicacion.comunes.controlador_base import ControladorBase

from .servicios import ServicioFacturaCompra

from .integracion import IntegracionFacturaCompra


class ControladorFacturaCompra(ControladorBase):

    servicio = ServicioFacturaCompra

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
    def obtener_completa(
        cls,
        id_registro,
    ):

        return cls.servicio.obtener_completa(
            id_registro,
        )

    @classmethod
    def preparar_desde_xml(
        cls,
        ruta_xml,
    ):

        return cls.servicio.preparar_desde_xml(
            ruta_xml,
        )

    @classmethod
    def importar_desde_xml(
        cls,
        ruta_xml,
    ):

        return cls.servicio.importar_desde_xml(
            ruta_xml,
        )

    @classmethod
    def validar_cufe_online(
        cls,
        id_registro,
    ):

        return IntegracionFacturaCompra.validar_cufe_online(
            id_registro,
        )

    @classmethod
    def contabilizar(
        cls,
        id_registro,
    ):

        return IntegracionFacturaCompra.contabilizar(
            id_registro,
        )

    @classmethod
    def aprobar_revision(
        cls,
        id_registro,
    ):

        return IntegracionFacturaCompra.aprobar_revision(
            id_registro,
        )

    @classmethod
    def generar_acuse_recibo(
        cls,
        id_registro,
        *,
        forzar=False,
    ):

        return IntegracionFacturaCompra.generar_acuse_recibo(
            id_registro,
            forzar=forzar,
        )

    @classmethod
    def contar_pendientes_revision(cls):

        return cls.servicio.repositorio.contar_pendientes_revision()

    @classmethod
    def sincronizar_dian(
        cls,
        *,
        fecha_desde=None,
        fecha_hasta=None,
    ):

        from aplicacion.integraciones.dian.servicio_recepcion import (
            ServicioRecepcionCompras,
        )

        return ServicioRecepcionCompras.sincronizar(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )
