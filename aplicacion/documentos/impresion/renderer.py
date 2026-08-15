from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.formatos_pagina import (
    FORMATOS_PAGINA,
)
from aplicacion.framework.reportes.motor_documento import (
    exportar_pdf_reporte,
    resolver_motor_pdf,
)
from aplicacion.framework.reportes.reporte_base import (
    ReporteDocumentoBase,
)


def resolver_formato_pagina(
    codigo: str | None,
) -> str:

    if (
        codigo
        and codigo in FORMATOS_PAGINA
    ):

        return codigo

    return "carta"


def exportar_documento_pdf(
    reporte: ReporteDocumentoBase,
    ruta: str | Path,
    *,
    formato_pagina: str | None = None,
    motor: str | None = None,
) -> str:

    return exportar_pdf_reporte(
        reporte,
        ruta,
        formato_pagina=formato_pagina,
        motor=motor,
    )


def abrir_centro_documento(
    reporte: ReporteDocumentoBase,
    *,
    parent=None,
    titulo: str = "",
):

    from aplicacion.framework.reportes.impresion_util import (
        abrir_centro_impresion,
    )

    return abrir_centro_impresion(
        reporte,
        parent=parent,
        titulo=titulo,
    )


def motor_resuelto(
    reporte: ReporteDocumentoBase,
    *,
    motor: str | None = None,
) -> str:

    return resolver_motor_pdf(
        reporte,
        motor=motor,
    )
