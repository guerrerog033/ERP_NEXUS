from __future__ import annotations

from aplicacion.dominio.documentos.consulta import consultar

from .result import DocumentoResult


class DocumentoService:
    """
    Fachada de compatibilidad — delega en ``dominio.documentos.consulta``.
    """

    @classmethod
    def buscar(
        cls,
        tipo_documento,
        numero_documento,
    ) -> DocumentoResult:
        return consultar(
            tipo_documento,
            numero_documento,
        )
