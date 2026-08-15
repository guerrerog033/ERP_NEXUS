from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorFacturaCompra


class FacturaCompraDataSource(SqlAlchemyDataSource):

    controlador = ControladorFacturaCompra

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

    def obtener_completa(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completa(
            id_registro,
        )

    def preparar_desde_xml(
        self,
        ruta_xml,
    ):

        return self.controlador.preparar_desde_xml(
            ruta_xml,
        )

    def importar_desde_xml(
        self,
        ruta_xml,
    ):

        return self.controlador.importar_desde_xml(
            ruta_xml,
        )

    def validar_cufe_online(
        self,
        id_registro,
    ):

        return self.controlador.validar_cufe_online(
            id_registro,
        )

    def contabilizar(
        self,
        id_registro,
    ):

        return self.controlador.contabilizar(
            id_registro,
        )

    def aprobar_revision(
        self,
        id_registro,
    ):

        return self.controlador.aprobar_revision(
            id_registro,
        )

    def generar_acuse_recibo(
        self,
        id_registro,
        *,
        forzar=False,
    ):

        return self.controlador.generar_acuse_recibo(
            id_registro,
            forzar=forzar,
        )

    def contar_pendientes_revision(
        self,
    ):

        return self.controlador.contar_pendientes_revision()

    def sincronizar_dian(
        self,
        *,
        fecha_desde=None,
        fecha_hasta=None,
    ):

        return self.controlador.sincronizar_dian(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )
