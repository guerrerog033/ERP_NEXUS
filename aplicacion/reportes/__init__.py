"""
Adaptadores de impresión por documento.

Los generadores concretos viven en ``aplicacion.reportes``; esta capa
expone el catálogo oficial y componentes reutilizables.
"""

from aplicacion.documentos.impresion.renderer import (
    abrir_centro_documento,
    exportar_documento_pdf,
)

__all__ = [
    "abrir_centro_documento",
    "exportar_documento_pdf",
]
