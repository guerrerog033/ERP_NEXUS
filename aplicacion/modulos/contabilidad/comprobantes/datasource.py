from aplicacion.framework.datasource import DataResult
from aplicacion.framework.datasource.datasource import DataSource

from .controlador import ControladorComprobante


class ComprobanteDataSource(DataSource):

    controlador = ControladorComprobante

    def listar(self, **kwargs):

        registros = self.controlador.listar()

        return DataResult(
            registros=registros,
            total=len(registros),
        )

    def buscar(self, texto):

        registros = self.controlador.buscar(
            texto,
        )

        return DataResult(
            registros=registros,
            total=len(registros),
        )

    def obtener(self, id_registro):

        return self.controlador.obtener(
            id_registro,
        )

    def obtener_por_id(self, id_registro):

        return self.obtener(
            id_registro,
        )

    def guardar(
        self,
        datos,
        id_registro=None,
    ):

        cabecera = datos.get(
            "cabecera",
            {},
        )

        lineas = datos.get(
            "lineas",
            [],
        )

        return self.controlador.guardar(
            cabecera,
            lineas,
            id_registro,
        )

    def eliminar(self, id_registro):

        return self.controlador.eliminar(
            id_registro,
        )

    def obtener_completo(self, id_registro):

        return self.obtener(
            id_registro,
        )
