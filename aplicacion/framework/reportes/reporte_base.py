from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class ReporteDocumentoBase(ABC):

    @property
    @abstractmethod
    def titulo_documento(
        self,
    ) -> str:
        ...

    @property
    @abstractmethod
    def numero_documento(
        self,
    ) -> str:
        ...

    @abstractmethod
    def generar_html(
        self,
    ) -> str:
        ...

    def nombre_archivo_pdf(
        self,
    ) -> str:

        numero = str(
            self.numero_documento or "",
        ).strip()

        return f"{self.titulo_documento} {numero}.pdf"

    def formato_pagina_predeterminado(
        self,
    ) -> str:

        return "carta"

    def soporta_pdf_reportlab(
        self,
    ) -> bool:

        return False

    def construir_pdf_reportlab(
        self,
        ruta: str | Path,
    ) -> Path:

        raise NotImplementedError(
            f"{type(self).__name__} no implementa PDF ReportLab.",
        )

    def formatos_pagina_disponibles(
        self,
    ) -> list[
        tuple[
            str,
            str,
        ]
    ]:

        from aplicacion.framework.reportes.formatos_pagina import (
            FORMATOS_PAGINA,
        )

        return [
            (
                str(
                    datos["etiqueta"],
                ),
                codigo,
            )
            for codigo, datos in FORMATOS_PAGINA.items()
        ]

    def correo_destinatario(
        self,
    ) -> str:

        return ""

    def telefono_destinatario(
        self,
    ) -> str:

        return ""

    def asunto_correo(
        self,
    ) -> str:

        return (
            f"{self.titulo_documento} "
            f"{self.numero_documento}"
        )

    def cuerpo_correo(
        self,
    ) -> str:

        return (
            f"Adjuntamos {self.titulo_documento.lower()} "
            f"{self.numero_documento}."
        )

    def texto_whatsapp(
        self,
    ) -> str:

        return (
            f"{self.titulo_documento} "
            f"{self.numero_documento}"
        )
