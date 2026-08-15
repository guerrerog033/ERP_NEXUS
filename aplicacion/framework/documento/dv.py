"""Re-export de dominio — mantener imports ``framework.documento.dv``."""

from aplicacion.dominio.documentos.dv import CalculadoraDV, DVCalculator

__all__ = [
    "CalculadoraDV",
    "DVCalculator",
]
