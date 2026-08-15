from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorNotaCreditoVenta


class NotaCreditoVentaDataSource(SqlAlchemyDataSource):

    controlador = ControladorNotaCreditoVenta

    def obtener_completa(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completa(
            id_registro,
        )

    def confirmar_generacion(
        self,
        id_registro,
        *,
        emitir_dian: bool = False,
    ):

        return self.controlador.confirmar_generacion(
            id_registro,
            emitir_dian=emitir_dian,
        )

    def emitir_electronica(
        self,
        id_registro,
    ):

        return self.controlador.emitir_electronica(
            id_registro,
        )

    def contabilizar(
        self,
        id_registro,
    ):

        return self.controlador.contabilizar(
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

    def crear_desde_factura(
        self,
        factura_id: int,
        motivo: str | None = None,
    ):

        return self.controlador.crear_desde_factura(
            factura_id,
            motivo,
        )
