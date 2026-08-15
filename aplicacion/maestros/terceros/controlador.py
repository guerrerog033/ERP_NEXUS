from aplicacion.comunes.controlador_base import ControladorBase

from .servicio import TerceroServicio


class TerceroControlador(ControladorBase):

    servicio = TerceroServicio

    # =====================================================
    # Documento
    # =====================================================

    @classmethod
    def documento_changed(
        cls,
        tipo_documento,
        numero_documento,
    ):

        return cls.obtener_servicio().documento_changed(

            tipo_documento,

            numero_documento,

        )