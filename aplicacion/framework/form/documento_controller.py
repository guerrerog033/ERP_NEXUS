from __future__ import annotations

from .documento_registry import DocumentoRegistry
from .documento_result import DocumentoResult


class DocumentoController:

    def procesar(
        self,
        tipo_documento,
        numero_documento,
    ) -> DocumentoResult:

        processor = DocumentoRegistry.obtener()

        if processor is None:

            return DocumentoResult(
                mensaje="No existe un procesador de documentos registrado."
            )

        return processor(
            tipo_documento,
            numero_documento,
        )