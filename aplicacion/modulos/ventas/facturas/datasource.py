from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorFacturaVenta


class FacturaVentaDataSource(SqlAlchemyDataSource):

    controlador = ControladorFacturaVenta

    def obtener_completa(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completa(
            id_registro,
        )

    def confirmar_venta(
        self,
        id_registro,
        *,
        emitir_dian: bool = False,
    ):

        return self.controlador.confirmar_venta(
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

    def actualizar_formato_impresion(
        self,
        id_registro,
        formato: str,
    ):

        return self.controlador.actualizar_formato_impresion(
            id_registro,
            formato,
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
