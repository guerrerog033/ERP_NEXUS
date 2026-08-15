from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorRemision


class RemisionDataSource(SqlAlchemyDataSource):

    controlador = ControladorRemision

    def confirmar_remision(
        self,
        id_registro: int,
    ):

        return self.controlador.confirmar_remision(
            id_registro,
        )

    def obtener_completa(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completa(
            id_registro,
        )

    def guardar_completa(
        self,
        cabecera,
        lineas,
        id_registro=None,
    ):

        return self.controlador.guardar_completa(
            cabecera,
            lineas,
            id_registro,
        )

    def despachar(
        self,
        id_registro,
    ):

        return self.controlador.despachar(
            id_registro,
        )
