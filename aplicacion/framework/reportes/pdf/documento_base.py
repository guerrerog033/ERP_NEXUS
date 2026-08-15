from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate


class DocumentoReportLab:

    paginas = LETTER

    margen_izquierdo = 15 * mm
    margen_derecho = 15 * mm
    margen_superior = 15 * mm
    margen_inferior = 18 * mm

    def __init__(
        self,
        archivo,
        empresa: dict,
    ):

        self.archivo = Path(
            archivo,
        )

        self.empresa = empresa

        self.story = []

    def crear_documento(
        self,
    ) -> BaseDocTemplate:

        ancho, alto = self.paginas

        frame = Frame(
            self.margen_izquierdo,
            self.margen_inferior,
            ancho
            - self.margen_izquierdo
            - self.margen_derecho,
            alto
            - self.margen_superior
            - self.margen_inferior,
            id="principal",
        )

        return BaseDocTemplate(
            str(
                self.archivo,
            ),
            pagesize=self.paginas,
            leftMargin=self.margen_izquierdo,
            rightMargin=self.margen_derecho,
            topMargin=self.margen_superior,
            bottomMargin=self.margen_inferior,
            pageTemplates=[
                PageTemplate(
                    id="principal",
                    frames=frame,
                    onPage=self._pie_pagina,
                )
            ],
        )

    def _pie_pagina(
        self,
        canvas,
        documento,
    ) -> None:

        canvas.saveState()

        canvas.setFont(
            "Helvetica",
            7,
        )

        canvas.setFillColorRGB(
            0.45,
            0.45,
            0.45,
        )

        canvas.drawCentredString(
            documento.pagesize[0] / 2,
            8 * mm,
            f"ERP NEXUS · Página {canvas.getPageNumber()}",
        )

        canvas.restoreState()

    def construir(
        self,
    ) -> Path:

        documento = self.crear_documento()

        self.armar()

        documento.build(
            self.story,
        )

        return self.archivo

    def armar(
        self,
    ) -> None:

        raise NotImplementedError
