from __future__ import annotations

from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QWidget,
)

from .centro_impresion import (
    CentroImpresionDialog,
)
from .documento_pdf import (
    DocumentoPdf,
)
from .reporte_base import (
    ReporteDocumentoBase,
)


def abrir_centro_impresion(
    reporte: ReporteDocumentoBase,
    *,
    parent: QWidget | None = None,
    titulo: str | None = None,
) -> None:

    documento = DocumentoPdf(
        reporte,
    )

    dialogo = CentroImpresionDialog(
        documento,
        parent=parent,
        titulo=titulo
        or (
            f"Centro de impresión — "
            f"{reporte.numero_documento}"
        ),
    )

    dialogo.exec()


def exportar_pdf_dialogo(
    reporte: ReporteDocumentoBase,
    *,
    parent: QWidget | None = None,
    formato_pagina: str | None = None,
) -> bool:

    documento = DocumentoPdf(
        reporte,
    )

    ruta, _filtro = QFileDialog.getSaveFileName(
        parent,
        "Exportar PDF",
        reporte.nombre_archivo_pdf(),
        "PDF (*.pdf)",
    )

    if not ruta:

        return False

    if not ruta.lower().endswith(
        ".pdf",
    ):

        ruta = f"{ruta}.pdf"

    documento.exportar_pdf(
        ruta,
        formato_pagina=(
            formato_pagina
            or reporte.formato_pagina_predeterminado()
        ),
    )

    if parent is not None:

        QMessageBox.information(
            parent,
            "PDF",
            f"Archivo guardado en:\n{ruta}",
        )

    return True
