from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .reporte_base import (
    ReporteDocumentoBase,
)


class ReporteDocumentoGenerico(
    ReporteDocumentoBase,
):

    def __init__(
        self,
        *,
        titulo: str,
        numero: str,
        generar_html_fn: Callable[[], str],
        nombre_pdf: str | None = None,
        correo_destino: str = "",
        telefono_destino: str = "",
        asunto_correo: str = "",
        cuerpo_correo: str = "",
        texto_whatsapp: str = "",
        formato_pagina: str = "carta",
        construir_pdf_reportlab_fn=None,
    ):

        self._titulo = titulo
        self._numero = numero
        self._generar_html_fn = generar_html_fn
        self._nombre_pdf = nombre_pdf
        self._correo_destino = correo_destino
        self._telefono_destino = telefono_destino
        self._asunto_correo = asunto_correo
        self._cuerpo_correo = cuerpo_correo
        self._texto_whatsapp = texto_whatsapp
        self._formato_pagina = formato_pagina
        self._construir_pdf_reportlab_fn = (
            construir_pdf_reportlab_fn
        )

    def soporta_pdf_reportlab(
        self,
    ) -> bool:

        return (
            self._construir_pdf_reportlab_fn
            is not None
        )

    def construir_pdf_reportlab(
        self,
        ruta: str | Path,
    ) -> Path:

        if (
            self._construir_pdf_reportlab_fn
            is None
        ):

            return super().construir_pdf_reportlab(
                ruta,
            )

        return self._construir_pdf_reportlab_fn(
            ruta,
        )

    @property
    def titulo_documento(
        self,
    ) -> str:

        return self._titulo

    @property
    def numero_documento(
        self,
    ) -> str:

        return self._numero

    def generar_html(
        self,
    ) -> str:

        return self._generar_html_fn()

    def nombre_archivo_pdf(
        self,
    ) -> str:

        if self._nombre_pdf:

            return self._nombre_pdf

        return super().nombre_archivo_pdf()

    def formato_pagina_predeterminado(
        self,
    ) -> str:

        return self._formato_pagina

    def correo_destinatario(
        self,
    ) -> str:

        return self._correo_destino

    def telefono_destinatario(
        self,
    ) -> str:

        return self._telefono_destino

    def asunto_correo(
        self,
    ) -> str:

        if self._asunto_correo:

            return self._asunto_correo

        return (
            f"{self._titulo} {self._numero}"
        )

    def cuerpo_correo(
        self,
    ) -> str:

        if self._cuerpo_correo:

            return self._cuerpo_correo

        return (
            f"Adjuntamos {self._titulo.lower()} "
            f"{self._numero}."
        )

    def texto_whatsapp(
        self,
    ) -> str:

        if self._texto_whatsapp:

            return self._texto_whatsapp

        return (
            f"{self._titulo} {self._numero}"
        )
