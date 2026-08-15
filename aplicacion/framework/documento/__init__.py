from .dv import DVCalculator
from .result import DocumentoResult

__all__ = [
    "DocumentoService",
    "DocumentoResult",
    "DVCalculator",
]


def __getattr__(name: str):

    if name == "DocumentoService":

        from .service import DocumentoService

        return DocumentoService

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}",
    )
