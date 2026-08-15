from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorDocumentoSoporte


class DocumentoSoporteDataSource(SqlAlchemyDataSource):

    controlador = ControladorDocumentoSoporte

    def obtener_completa(
        self,
        id_registro,
    ):

        return self.controlador.obtener_completa(
            id_registro,
        )

    def emitir_electronica(
        self,
        id_registro,
    ):

        return self.controlador.emitir_electronica(
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
