from aplicacion.framework.crud.crud_documento import CrudDocumento
from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.modulos.tesoreria.recibos_caja.datasource import (
    ReciboCajaDataSource,
)
from aplicacion.modulos.tesoreria.recibos_caja.formulario import (
    FormularioReciboCaja,
)
from aplicacion.modulos.tesoreria.recibos_caja.vista_recibo import (
    VistaReciboCaja,
)


class MaestroRecibosCaja(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Recibos de caja"

    titulo_singular = "Recibo de caja"

    datasource = ReciboCajaDataSource

    formulario = FormularioReciboCaja

    vista_documento = VistaReciboCaja

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        recibo = self.datasource.obtener_completo(
            id_registro,
        )

        if recibo is None:

            return "Recibo de caja"

        return f"Recibo {recibo.numero}"
