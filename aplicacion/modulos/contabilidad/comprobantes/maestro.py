from aplicacion.framework.crud.crud_documento import CrudDocumento
from aplicacion.framework.crud.crud_master import CrudMaster

from .comprobante_definition import ComprobanteDefinition
from .datasource import ComprobanteDataSource
from .formulario import FormularioComprobante
from .vista_comprobante import VistaComprobante


class FormularioComprobanteLista:

    definition = ComprobanteDefinition


class MaestroComprobantes(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Comprobantes contables"

    titulo_singular = "Comprobante contable"

    datasource = ComprobanteDataSource

    formulario = FormularioComprobanteLista

    vista_documento = VistaComprobante

    def __init__(self):

        super().__init__()

    def editar(self):

        id_registro = (
            self.obtener_id_seleccionado()
        )

        if id_registro is None:

            self.mostrar_error(
                "Seleccione un registro.",
            )

            return

        asiento = self.datasource.obtener_completo(
            id_registro,
        )

        if (
            asiento is not None
            and asiento.origen == "manual"
        ):

            self._mostrar_dialogo_formulario(
                id_registro=id_registro,
            )

            return

        super().editar()

    def eliminar(self):

        id_registro = (
            self.obtener_id_seleccionado()
        )

        if id_registro is None:

            self.mostrar_error(
                "Seleccione un registro.",
            )

            return

        asiento = self.datasource.obtener_completo(
            id_registro,
        )

        if (
            asiento is not None
            and asiento.origen != "manual"
        ):

            self.mostrar_error(
                "Solo puede eliminar comprobantes manuales.",
            )

            return

        super().eliminar()

    def crear_formulario(
        self,
        id_registro=None,
        parent=None,
    ):

        return FormularioComprobante(
            id_registro=id_registro,
            parent=parent,
        )

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        asiento = self.datasource.obtener_completo(
            id_registro,
        )

        if asiento is None:

            return "Comprobante contable"

        return f"Comprobante {asiento.numero}"
