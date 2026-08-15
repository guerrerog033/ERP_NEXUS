from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorComprobanteEgreso


class ComprobanteEgresoDataSource(SqlAlchemyDataSource):

    controlador = ControladorComprobanteEgreso

    def obtener_completo(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completo(
            id_registro,
        )

    def listar_facturas_pendientes(
        self,
        proveedor_id: int,
    ):

        return self.controlador.listar_facturas_pendientes(
            proveedor_id,
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
