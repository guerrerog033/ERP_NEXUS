from aplicacion.framework.crud.crud_documento import CrudDocumento
from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.modulos.tesoreria.comprobantes_egreso.datasource import (
    ComprobanteEgresoDataSource,
)
from aplicacion.modulos.tesoreria.comprobantes_egreso.formulario import (
    FormularioComprobanteEgreso,
)
from aplicacion.modulos.tesoreria.comprobantes_egreso.vista_comprobante import (
    VistaComprobanteEgreso,
)


class MaestroComprobantesEgreso(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Comprobantes de egreso"

    titulo_singular = "Comprobante de egreso"

    datasource = ComprobanteEgresoDataSource

    formulario = FormularioComprobanteEgreso

    vista_documento = VistaComprobanteEgreso

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        comprobante = self.datasource.obtener_completo(
            id_registro,
        )

        if comprobante is None:

            return "Comprobante de egreso"

        return f"Comprobante {comprobante.numero}"
