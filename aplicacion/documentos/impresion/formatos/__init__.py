from __future__ import annotations

from aplicacion.documentos.impresion.documento_base import (
    DocumentoReportLabAdapter,
)
from aplicacion.reportes.compras.pdf.factura_compra import (
    FacturaCompraPDF,
)
from aplicacion.reportes.compras.pdf.orden_compra import (
    OrdenCompraPDF,
)
from aplicacion.reportes.tesoreria.pdf.comprobante_egreso import (
    ComprobanteEgresoPDF,
)
from aplicacion.reportes.tesoreria.pdf.recibo_caja import (
    ReciboCajaPDF,
)
from aplicacion.reportes.ventas.pdf.cotizacion import (
    CotizacionPDF,
)
from aplicacion.reportes.ventas.pdf.factura_venta import (
    FacturaVentaPDF,
)
from aplicacion.reportes.ventas.pdf.nota_venta import (
    NotaVentaPDF,
)
from aplicacion.reportes.ventas.pdf.pedido import (
    PedidoVentaPDF,
)
from aplicacion.reportes.ventas.pdf.remision import (
    RemisionPDF,
)


class RendererFacturaVenta(
    DocumentoReportLabAdapter,
):

    codigo_catalogo = "04_FACTURA_VENTA"
    titulo_documento = "FACTURA ELECTRÓNICA DE VENTA"
    clase_pdf = FacturaVentaPDF


class RendererCotizacion(
    DocumentoReportLabAdapter,
):

    codigo_catalogo = "01_COTIZACION"
    titulo_documento = "COTIZACIÓN"
    clase_pdf = CotizacionPDF


class RendererPedidoVenta(
    DocumentoReportLabAdapter,
):

    codigo_catalogo = "02_PEDIDO_VENTA"
    titulo_documento = "PEDIDO DE VENTA"
    clase_pdf = PedidoVentaPDF


class RendererNotaCredito(
    DocumentoReportLabAdapter,
):

    codigo_catalogo = "05_NOTA_CREDITO"
    titulo_documento = "NOTA CRÉDITO DE VENTA"
    clase_pdf = NotaVentaPDF


class RendererNotaDebito(
    DocumentoReportLabAdapter,
):

    codigo_catalogo = "06_NOTA_DEBITO"
    titulo_documento = "NOTA DÉBITO DE VENTA"
    clase_pdf = NotaVentaPDF


class RendererRemision(
    DocumentoReportLabAdapter,
):

    codigo_catalogo = "03_REMISION"
    titulo_documento = "REMISIÓN"
    clase_pdf = RemisionPDF


class RendererReciboCaja(
    DocumentoReportLabAdapter,
):

    codigo_catalogo = "07_RECIBO_CAJA"
    titulo_documento = "RECIBO DE CAJA"
    clase_pdf = ReciboCajaPDF


class RendererComprobanteEgreso(
    DocumentoReportLabAdapter,
):

    codigo_catalogo = "13_COMPROBANTE_EGRESO"
    titulo_documento = "COMPROBANTE DE EGRESO"
    clase_pdf = ComprobanteEgresoPDF


class RendererFacturaCompra(
    DocumentoReportLabAdapter,
):

    codigo_catalogo = "11_FACTURA_COMPRA"
    titulo_documento = "FACTURA DE COMPRA"
    clase_pdf = FacturaCompraPDF


class RendererOrdenCompra(
    DocumentoReportLabAdapter,
):

    codigo_catalogo = "09_ORDEN_COMPRA"
    titulo_documento = "ORDEN DE COMPRA"
    clase_pdf = OrdenCompraPDF


RENDERERS: dict[
    str,
    type[DocumentoReportLabAdapter],
] = {
    "01_COTIZACION": RendererCotizacion,
    "02_PEDIDO_VENTA": RendererPedidoVenta,
    "03_REMISION": RendererRemision,
    "04_FACTURA_VENTA": RendererFacturaVenta,
    "05_NOTA_CREDITO": RendererNotaCredito,
    "06_NOTA_DEBITO": RendererNotaDebito,
    "07_RECIBO_CAJA": RendererReciboCaja,
    "09_ORDEN_COMPRA": RendererOrdenCompra,
    "11_FACTURA_COMPRA": RendererFacturaCompra,
    "13_COMPROBANTE_EGRESO": RendererComprobanteEgreso,
}


def crear_renderer(
    codigo: str,
    datos: dict,
    *,
    archivo,
    titulo: str | None = None,
    electronica: bool = False,
) -> DocumentoReportLabAdapter:

    clase = RENDERERS.get(
        codigo,
    )

    if clase is None:

        raise KeyError(
            f"No hay renderer ReportLab para {codigo}.",
        )

    renderer = clase(
        datos,
        archivo=archivo,
    )

    if titulo:

        renderer.titulo = titulo

    renderer.electronica = electronica

    return renderer
