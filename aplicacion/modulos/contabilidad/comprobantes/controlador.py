from aplicacion.comunes.controlador_base import ControladorBase

from aplicacion.modulos.contabilidad.servicio_comprobantes import (
    ServicioComprobantes,
)


class ControladorComprobante(ControladorBase):

    servicio = ServicioComprobantes

    @classmethod
    def listar(cls, **kwargs):

        return cls.servicio.listar()

    @classmethod
    def buscar(cls, texto):

        return cls.servicio.buscar(
            texto,
        )

    @classmethod
    def obtener(cls, id_registro):

        return cls.servicio.obtener_completo(
            id_registro,
        )

    @classmethod
    def guardar(
        cls,
        cabecera,
        lineas,
        id_registro=None,
    ):

        return cls.servicio.guardar_manual(
            cabecera,
            lineas,
            id_registro,
        )

    @classmethod
    def eliminar(cls, id_registro):

        return cls.servicio.eliminar_manual(
            id_registro,
        )
