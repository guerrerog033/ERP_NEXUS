from aplicacion.framework.datasource import SqlAlchemyDataSource

from .controlador import ControladorGuiaRemisionElectronica


class GuiaRemisionElectronicaDataSource(SqlAlchemyDataSource):

    controlador = ControladorGuiaRemisionElectronica

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

    def crear_desde_remision(
        self,
        remision_id: int,
        **kwargs,
    ):

        return self.controlador.crear_desde_remision(
            remision_id,
            **kwargs,
        )
