from .consulta_base import ConsultaDocumento
from ..documento_result import DocumentoResult


class ConsultaAPI(ConsultaDocumento):

    def consultar(
        self,
        tipo_documento,
        numero_documento,
    ):

        return DocumentoResult(
            tipo=tipo_documento,
            numero=numero_documento,
        )