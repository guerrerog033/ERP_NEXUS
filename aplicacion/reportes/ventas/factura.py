from __future__ import annotations

from pathlib import Path

from aplicacion.framework.reportes.reporte_base import (
    ReporteDocumentoBase,
)


class ReporteFacturaVenta(
    ReporteDocumentoBase,
):

    def __init__(
        self,
        factura,
        detalles,
        nombre_cliente: str,
        *,
        formato: str | None = None,
    ):

        self.factura = factura
        self.detalles = detalles
        self.nombre_cliente = nombre_cliente
        self.formato = formato

    @property
    def titulo_documento(
        self,
    ) -> str:

        return "Factura de venta"

    @property
    def numero_documento(
        self,
    ) -> str:

        return str(
            getattr(
                self.factura,
                "numero",
                "",
            )
            or "",
        )

    def generar_html(
        self,
    ) -> str:

        from aplicacion.modulos.ventas.facturas.formatos_impresion import (
            generar_html_factura_venta,
        )

        return generar_html_factura_venta(
            self.factura,
            self.detalles,
            self.nombre_cliente,
            formato=self.formato,
        )

    def nombre_archivo_pdf(
        self,
    ) -> str:

        from aplicacion.modulos.ventas.facturas.impresion import (
            nombre_archivo_pdf_factura,
        )

        return nombre_archivo_pdf_factura(
            self.factura,
            self.nombre_cliente,
        )

    def soporta_pdf_reportlab(
        self,
    ) -> bool:

        return True

    def construir_pdf_reportlab(
        self,
        ruta: str | Path,
    ) -> Path:

        from aplicacion.reportes.comunes.datos_documento import (
            empresa_reporte,
            factura_venta_a_dto,
        )
        from aplicacion.reportes.ventas.pdf.factura_venta import (
            FacturaVentaPDF,
        )

        dto = factura_venta_a_dto(
            self.factura,
            self.detalles,
            self.nombre_cliente,
            electronica=False,
        )

        return FacturaVentaPDF(
            ruta,
            empresa_reporte(),
            dto,
            titulo="FACTURA DE VENTA",
            electronica=False,
        ).construir()
