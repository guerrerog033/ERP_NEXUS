from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from ..documento_result import DocumentoResult


class ConsultaDocumento(ABC):
    """
    Clase base para cualquier proveedor
    de consulta de documentos.

    Ejemplos:

        • Base de datos local
        • DIAN
        • RUES
        • API externa
    """

    @abstractmethod
    def consultar(
        self,
        tipo_documento: str,
        numero_documento: str,
    ) -> DocumentoResult:

        pass