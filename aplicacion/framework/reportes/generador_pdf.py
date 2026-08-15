from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import (
    QTextDocument,
)
from PySide6.QtPrintSupport import (
    QPrintDialog,
    QPrinter,
)
from PySide6.QtWidgets import (
    QWidget,
)

from .formatos_pagina import (
    aplicar_formato_pagina,
)


def html_a_documento(
    html: str,
) -> QTextDocument:

    documento = QTextDocument()

    documento.setHtml(
        html,
    )

    return documento


def _crear_impresora(
    *,
    ruta_pdf: str | None = None,
    formato_pagina: str = "carta",
) -> QPrinter:

    impresora = QPrinter(
        QPrinter.PrinterMode.HighResolution,
    )

    if ruta_pdf:

        impresora.setOutputFormat(
            QPrinter.OutputFormat.PdfFormat,
        )

        impresora.setOutputFileName(
            ruta_pdf,
        )

    aplicar_formato_pagina(
        impresora,
        formato_pagina,
    )

    return impresora


def imprimir_html(
    html: str,
    *,
    parent: QWidget | None = None,
    formato_pagina: str = "carta",
) -> bool:

    documento = html_a_documento(
        html,
    )

    impresora = _crear_impresora(
        formato_pagina=formato_pagina,
    )

    dialogo = QPrintDialog(
        impresora,
        parent,
    )

    if dialogo.exec() != QPrintDialog.DialogCode.Accepted:

        return False

    documento.print(
        impresora,
    )

    return True


def exportar_html_pdf(
    html: str,
    ruta_pdf: str | Path,
    *,
    formato_pagina: str = "carta",
) -> str:

    destino = str(
        ruta_pdf,
    )

    documento = html_a_documento(
        html,
    )

    impresora = _crear_impresora(
        ruta_pdf=destino,
        formato_pagina=formato_pagina,
    )

    documento.print(
        impresora,
    )

    return destino
