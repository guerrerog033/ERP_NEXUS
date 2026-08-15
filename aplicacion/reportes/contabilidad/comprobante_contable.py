from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_generico import (
    ReporteDocumentoGenerico,
)
from aplicacion.modulos.contabilidad.comprobantes.formatos_impresion import (
    generar_html_comprobante_contable,
)


def _construir_pdf_comprobante_contable(
    asiento,
    ruta: str | Path,
) -> Path:

    from aplicacion.reportes.comunes.datos_contabilidad import (
        comprobante_contable_a_dto,
    )
    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
    )
    from aplicacion.reportes.contabilidad.pdf.comprobante_contable import (
        ComprobanteContablePDF,
    )

    dto = comprobante_contable_a_dto(
        asiento,
    )

    return ComprobanteContablePDF(
        ruta,
        empresa_reporte(),
        dto,
    ).construir()


def crear_reporte_comprobante_contable(
    asiento,
) -> ReporteDocumentoGenerico:

    numero = str(
        asiento.numero or "",
    )

    return ReporteDocumentoGenerico(
        titulo="Comprobante contable",
        numero=numero,
        generar_html_fn=lambda: generar_html_comprobante_contable(
            asiento,
        ),
        nombre_pdf=f"Comprobante {numero}.pdf",
        construir_pdf_reportlab_fn=lambda ruta: _construir_pdf_comprobante_contable(
            asiento,
            ruta,
        ),
    )
