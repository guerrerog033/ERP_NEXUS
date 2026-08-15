from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from reportlab.lib.pagesizes import LETTER

from aplicacion.documentos.impresion.documento_datos import (
    DocumentoDatos,
    documento_datos_a_dict,
)
from aplicacion.framework.reportes.formatos_pagina import (
    FORMATOS_PAGINA,
)
from aplicacion.framework.reportes.pdf.documento_base import (
    DocumentoReportLab,
)


def pagina_reportlab(
    codigo_formato: str,
):

    datos = FORMATOS_PAGINA.get(
        codigo_formato,
        FORMATOS_PAGINA["carta"],
    )

    ancho_mm = float(
        datos["ancho_mm"],
    )

    alto_mm = float(
        datos["alto_mm"],
    )

    if (
        codigo_formato == "carta"
        or (
            abs(
                ancho_mm - 215.9,
            )
            < 1
            and abs(
                alto_mm - 279.4,
            )
            < 1
        )
    ):

        return LETTER

    from reportlab.lib.units import mm

    return (
        ancho_mm * mm,
        alto_mm * mm,
    )


class DocumentoRendererBase(
    ABC,
):

    codigo_catalogo: str = ""
    titulo_documento: str = ""
    formato_pagina: str = "carta"

    def __init__(
        self,
        datos: DocumentoDatos | dict,
        *,
        archivo: str | Path,
    ):

        if isinstance(
            datos,
            dict,
        ):

            self.datos = datos

            self._modelo = None

        else:

            self._modelo = datos

            self.datos = documento_datos_a_dict(
                datos,
            )

        self.archivo = Path(
            archivo,
        )

    @abstractmethod
    def construir_pdf(
        self,
    ) -> Path:
        ...

    def empresa(
        self,
    ) -> dict:

        return self.datos.get(
            "empresa",
            {},
        )


class DocumentoReportLabAdapter(
    DocumentoRendererBase,
):

    clase_pdf: type[DocumentoReportLab] | None = None
    titulo: str = ""
    electronica: bool = False
    argumento_payload: str = "factura"

    def construir_pdf(
        self,
    ) -> Path:

        if self.clase_pdf is None:

            raise NotImplementedError(
                f"{type(self).__name__} no define clase_pdf.",
            )

        instancia = self.clase_pdf(
            self.archivo,
            self.empresa(),
            self.datos,
            titulo=self.titulo
            or self.titulo_documento,
            electronica=self.electronica,
        )

        instancia.paginas = pagina_reportlab(
            self.formato_pagina,
        )

        return instancia.construir()
