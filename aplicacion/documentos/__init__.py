"""
Dominio de representación gráfica de documentos comerciales, financieros
e inventario (PDF, vista previa, impresión y correo).

La implementación vive en ``aplicacion.documentos.impresion``.
Los adaptadores por módulo siguen en ``aplicacion.reportes``.
"""

from aplicacion.documentos.impresion.catalogo import (
    CATALOGO_DOCUMENTOS,
    CodigoDocumento,
)

__all__ = [
    "CATALOGO_DOCUMENTOS",
    "CodigoDocumento",
]
