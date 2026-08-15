from aplicacion.framework.crud.crud_documento import CrudDocumento
from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.modulos.compras.documentos_soporte.datasource import (
    DocumentoSoporteDataSource,
)
from aplicacion.modulos.compras.documentos_soporte.formulario import (
    FormularioDocumentoSoporte,
)
from aplicacion.modulos.compras.documentos_soporte.vista import (
    VistaDocumentoSoporte,
)


class MaestroDocumentosSoporte(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Documentos soporte"

    titulo_singular = "Documento soporte"

    datasource = DocumentoSoporteDataSource

    formulario = FormularioDocumentoSoporte

    vista_documento = VistaDocumentoSoporte

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        documento = self.datasource.obtener_completa(
            id_registro,
        )

        if documento is None:

            return "Documento soporte"

        return f"Documento soporte {documento.numero}"

    def _titulo_dialogo_formulario(
        self,
        id_registro=None,
    ) -> str:

        if id_registro is not None:

            return "Editar documento soporte"

        return "Nuevo documento soporte"
