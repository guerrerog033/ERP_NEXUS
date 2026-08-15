from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import (
    QMarginsF,
    QSizeF,
    Qt,
)
from PySide6.QtGui import (
    QPageLayout,
    QPageSize,
    QTextDocument,
)
from PySide6.QtPrintSupport import (
    QPrintDialog,
    QPrinter,
)
from PySide6.QtWidgets import (
    QMessageBox,
    QWidget,
)


def _formatear_moneda(
    valor,
) -> str:

    return f"${float(valor or 0):,.0f}"


def generar_html_ticket_pos(
    *,
    factura_numero: str,
    cliente: str,
    lineas: list[dict],
    total: float,
    recibido: float,
    cambio: float,
    metodo_pago: str,
    usuario: str,
) -> str:

    filas_producto = []

    for linea in lineas:

        descripcion = str(
            linea.get(
                "descripcion",
                "",
            )
            or "Producto",
        )

        cantidad = float(
            linea.get(
                "cantidad",
                0,
            )
            or 0,
        )

        precio = float(
            linea.get(
                "precio_unitario",
                0,
            )
            or 0,
        )

        total_linea = float(
            linea.get(
                "total_linea",
                cantidad * precio,
            )
            or 0,
        )

        filas_producto.append(
            f"""
            <tr>
                <td>{descripcion}</td>
                <td align="right">{cantidad:.2f}</td>
                <td align="right">{_formatear_moneda(total_linea)}</td>
            </tr>
            """,
        )

    ahora = datetime.now().strftime(
        "%Y-%m-%d %H:%M",
    )

    return f"""
    <html>
    <head>
    <style>
        body {{
            font-family: Consolas, monospace;
            font-size: 9pt;
            color: #111827;
        }}
        h3 {{
            text-align: center;
            margin: 0 0 8px 0;
        }}
        .meta {{
            font-size: 8pt;
            margin-bottom: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        td {{
            padding: 2px 0;
            vertical-align: top;
        }}
        .totales {{
            margin-top: 8px;
            border-top: 1px dashed #9CA3AF;
            padding-top: 6px;
        }}
        .totales td {{
            font-weight: 700;
        }}
    </style>
    </head>
    <body>
        <h3>ERP NEXUS POS</h3>
        <div class="meta">
            Factura: {factura_numero}<br/>
            Cliente: {cliente or '—'}<br/>
            Fecha: {ahora}<br/>
            Cajero: {usuario or 'sistema'}<br/>
            Pago: {metodo_pago.replace('_', ' ').title()}
        </div>
        <table>
            {"".join(filas_producto)}
        </table>
        <table class="totales">
            <tr><td>Total</td><td align="right">{_formatear_moneda(total)}</td></tr>
            <tr><td>Recibido</td><td align="right">{_formatear_moneda(recibido)}</td></tr>
            <tr><td>Cambio</td><td align="right">{_formatear_moneda(cambio)}</td></tr>
        </table>
        <p style="text-align:center;margin-top:10px;">Gracias por su compra</p>
    </body>
    </html>
    """


def imprimir_ticket_pos(
    *,
    factura_numero: str,
    cliente: str,
    lineas: list[dict],
    total: float,
    recibido: float,
    cambio: float,
    metodo_pago: str,
    usuario: str,
    parent: QWidget | None = None,
) -> bool:

    documento = QTextDocument()
    documento.setHtml(
        generar_html_ticket_pos(
            factura_numero=factura_numero,
            cliente=cliente,
            lineas=lineas,
            total=total,
            recibido=recibido,
            cambio=cambio,
            metodo_pago=metodo_pago,
            usuario=usuario,
        ),
    )

    impresora = QPrinter(
        QPrinter.PrinterMode.HighResolution,
    )

    ancho_ticket = QPageSize(
        QSizeF(
            80,
            297,
        ),
        QPageSize.Unit.Millimeter,
        "Ticket80",
        QPageSize.SizeMatchPolicy.ExactMatch,
    )

    impresora.setPageSize(
        ancho_ticket,
    )

    impresora.setPageOrientation(
        QPageLayout.Orientation.Portrait,
    )

    impresora.setPageMargins(
        QMarginsF(
            2,
            2,
            2,
            2,
        ),
        QPageLayout.Unit.Millimeter,
    )

    dialogo = QPrintDialog(
        impresora,
        parent,
    )

    dialogo.setWindowTitle(
        "Imprimir ticket POS",
    )

    if (
        dialogo.exec()
        != QPrintDialog.DialogCode.Accepted
    ):

        return False

    documento.print_(
        impresora,
    )

    QMessageBox.information(
        parent,
        "Ticket POS",
        "Ticket enviado a la impresora.",
    )

    return True
