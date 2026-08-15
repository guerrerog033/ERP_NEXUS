from .consulta import consultar, obtener_procesador, registrar
from .dv import CalculadoraDV, DVCalculator
from .resultado import DocumentoResult
from .servicio import ServicioDocumento

__all__ = [
    "CalculadoraDV",
    "DVCalculator",
    "DocumentoResult",
    "ServicioDocumento",
    "consultar",
    "obtener_procesador",
    "registrar",
]
