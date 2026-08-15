from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)

from .controlador import ControladorCotizacion


class CotizacionDataSource(SqlAlchemyDataSource):

    controlador = ControladorCotizacion

    def confirmar_cotizacion(
        self,
        id_registro: int,
    ):

        return self.controlador.confirmar_cotizacion(
            id_registro,
        )

    def guardar_completa(        self,
        cabecera,
        lineas,
        id_registro=None,
    ):

        return self.controlador.guardar_completa(
            cabecera,
            lineas,
            id_registro,
        )

    def obtener_completa(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completa(
            id_registro,
        )
