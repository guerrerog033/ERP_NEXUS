from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QWidget

from .generador_pdf import (
    exportar_html_pdf,
    imprimir_html,
)
from .reporte_base import (
    ReporteDocumentoBase,
)


class DocumentoPdf:

    def __init__(
        self,
        reporte: ReporteDocumentoBase,
    ):

        self.reporte = reporte

    @property
    def html(
        self,
    ) -> str:

        return self.reporte.generar_html()

    def imprimir(
        self,
        *,
        parent: QWidget | None = None,
        formato_pagina: str | None = None,
    ) -> bool:

        return imprimir_html(
            self.html,
            parent=parent,
            formato_pagina=(
                formato_pagina
                or self.reporte.formato_pagina_predeterminado()
            ),
        )

    def exportar_pdf(
        self,
        ruta: str | Path,
        *,
        formato_pagina: str | None = None,
        motor: str | None = None,
    ) -> str:

        from .motor_documento import (
            exportar_pdf_reporte,
        )

        return exportar_pdf_reporte(
            self.reporte,
            ruta,
            formato_pagina=formato_pagina,
            motor=motor,
        )
