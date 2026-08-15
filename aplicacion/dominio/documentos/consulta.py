from __future__ import annotations

from typing import Callable

from .resultado import DocumentoResult

ProcesadorDocumento = Callable[
    [object, object],
    DocumentoResult,
]

_procesador: ProcesadorDocumento | None = None


def registrar(
    procesador: ProcesadorDocumento,
) -> None:
    global _procesador
    _procesador = procesador


def obtener_procesador() -> ProcesadorDocumento | None:
    return _procesador


def consultar(
    tipo_documento,
    numero_documento,
) -> DocumentoResult:
    if _procesador is None:
        return DocumentoResult(
            tipo=str(
                tipo_documento or "",
            ),
            numero=str(
                numero_documento or "",
            ),
            mensaje=(
                "No hay procesador de documentos registrado."
            ),
        )

    return _procesador(
        tipo_documento,
        numero_documento,
    )
