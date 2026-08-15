from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorReciboCaja


class ReciboCajaDataSource(SqlAlchemyDataSource):

    controlador = ControladorReciboCaja

    def obtener_completo(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completo(
            id_registro,
        )

    def listar_facturas_pendientes(
        self,
        cliente_id: int,
    ):

        return self.controlador.listar_facturas_pendientes(
            cliente_id,
        )

    def guardar_completo(
        self,
        cabecera,
        lineas,
        *,
        id_registro=None,
    ):

        return self.controlador.guardar_completo(
            cabecera,
            lineas,
            id_registro=id_registro,
        )

    def contabilizar(
        self,
        id_registro,
    ):

        return self.controlador.contabilizar(
            id_registro,
        )
