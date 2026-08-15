from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from PySide6.QtCore import QUrl, QSizeF
from PySide6.QtGui import (
    QDesktopServices,
    QPageSize,
    QTextDocument,
)
from PySide6.QtPrintSupport import (
    QPrintDialog,
    QPrintPreviewDialog,
    QPrinter,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QWidget,
)

from aplicacion.maestros.productos.servicios import (
    ServicioProducto,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    generar_html_cotizacion,
    normalizar_formato_codigo,
)
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)
from aplicacion.nucleo.configuracion import Configuracion


def _formatear_moneda(
    valor: float,
) -> str:

    return f"${valor:,.2f}"


def _sanitizar_nombre_archivo(
    texto: str,
) -> str:

    prohibidos = '<>:"/\\|?*'

    limpio = "".join(
        " "
        if caracter in prohibidos
        else caracter
        for caracter in str(
            texto or "",
        )
    )

    return " ".join(
        limpio.split(),
    ).strip()


def nombre_archivo_pdf_cotizacion(
    cotizacion,
    nombre_cliente: str,
) -> str:

    numero = str(
        getattr(
            cotizacion,
            "numero",
            "",
        )
        or "",
    ).strip()

    cliente = _sanitizar_nombre_archivo(
        nombre_cliente,
    )

    titulo = f"Cotización No. {numero}"

    if cliente:

        return f"{titulo} {cliente}.pdf"

    return f"{titulo}.pdf"


def _lineas_desde_detalles(
    detalles,
) -> list[dict]:

    lineas = []

    for detalle in detalles:

        lineas.append(
            {
                "producto_id": detalle.producto_id,
                "descripcion": detalle.descripcion,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "impuesto_id": detalle.impuesto_id,
                "precio_incluye_iva": bool(
                    getattr(
                        detalle,
                        "precio_incluye_iva",
                        False,
                    )
                ),
            },
        )

    return lineas


def _resumen_cotizacion(
    cotizacion,
    detalles,
) -> dict:

    return ServicioCotizacion._calcular_resumen(
        _lineas_desde_detalles(
            detalles,
        ),
        getattr(
            cotizacion,
            "retefuente_id",
            None,
        ),
        getattr(
            cotizacion,
            "reteica_id",
            None,
        ),
        getattr(
            cotizacion,
            "reteiva_id",
            None,
        ),
    )


def _codigo_producto(
    producto_id,
    descripcion: str,
) -> str:

    if producto_id:

        producto = ServicioProducto.obtener_por_id(
            producto_id,
        )

        if (
            producto is not None
            and producto.codigo
        ):

            return producto.codigo

    if " - " in descripcion:

        return descripcion.split(
            " - ",
            1,
        )[0]

    return ""


def _html_cotizacion(
    cotizacion,
    detalles,
    nombre_cliente: str,
) -> str:

    return generar_html_cotizacion(
        cotizacion,
        detalles,
        nombre_cliente,
    )


def _texto_resumen_cotizacion(
    cotizacion,
    detalles,
    nombre_cliente: str,
) -> str:

    resumen = _resumen_cotizacion(
        cotizacion,
        detalles,
    )

    lineas_texto = []

    for detalle in detalles:

        codigo = _codigo_producto(
            detalle.producto_id,
            detalle.descripcion,
        )

        prefijo = f"{codigo} - " if codigo else ""

        lineas_texto.append(
            f"• {prefijo}{detalle.descripcion}: "
            f"{detalle.cantidad:g} x "
            f"{_formatear_moneda(detalle.precio_unitario)} = "
            f"{_formatear_moneda(detalle.total_linea)}",
        )

    mensaje = [
        f"Cotización {cotizacion.numero}",
        f"Fecha: {cotizacion.fecha.strftime('%d/%m/%Y')}",
        f"Cliente: {nombre_cliente}",
        "",
        *lineas_texto,
        "",
        f"Subtotal: {_formatear_moneda(resumen['subtotal'])}",
    ]

    if resumen["retefuente"] > 0:

        mensaje.append(
            f"Retefuente: {_formatear_moneda(resumen['retefuente'])}",
        )

    if resumen["reteica"] > 0:

        mensaje.append(
            f"ReteICA: {_formatear_moneda(resumen['reteica'])}",
        )

    if resumen.get(
        "reteiva",
        0,
    ) > 0:

        mensaje.append(
            f"ReteIVA: {_formatear_moneda(resumen['reteiva'])}",
        )

    mensaje.append(
        f"Total: {_formatear_moneda(resumen['total'])}",
    )

    if cotizacion.observaciones:

        mensaje.extend(
            [
                "",
                f"Observaciones: {cotizacion.observaciones}",
            ],
        )

    return "\n".join(
        mensaje,
    )


def _crear_documento(
    cotizacion,
    detalles,
    nombre_cliente: str,
) -> QTextDocument:

    html = _html_cotizacion(
        cotizacion,
        detalles,
        nombre_cliente,
    )

    documento = QTextDocument()

    documento.setDocumentMargin(
        24,
    )

    documento.setHtml(
        html,
    )

    return documento


def _configurar_impresora(
    cotizacion,
    impresora: QPrinter,
    ruta_pdf: str | None = None,
) -> None:

    if ruta_pdf:

        impresora.setOutputFormat(
            QPrinter.OutputFormat.PdfFormat,
        )

        impresora.setOutputFileName(
            ruta_pdf,
        )

    formato = normalizar_formato_codigo(
        cotizacion.formato_impresion,
    )

    if formato == "tirilla":

        ancho_mm = float(
            Configuracion.obtener(
                "impresion",
                "ancho_tirilla_mm",
            )
            or 80,
        )

        impresora.setPageSize(
            QPageSize(
                QSizeF(
                    ancho_mm,
                    297.0,
                ),
                QPageSize.Unit.Millimeter,
            ),
        )

        return

    if formato == "compacto":

        impresora.setPageSize(
            QPageSize(
                QPageSize.PageSizeId.A5,
            ),
        )

        return


def _ruta_reportes() -> Path:

    ruta = Configuracion.obtener(
        "reportes",
        "ruta",
    )

    if not ruta:

        ruta = "reportes"

    carpeta = Path(
        ruta,
    )

    carpeta.mkdir(
        parents=True,
        exist_ok=True,
    )

    return carpeta


def generar_pdf_cotizacion(
    cotizacion,
    detalles,
    nombre_cliente: str,
    ruta_destino: str | Path,
    parent: QWidget | None = None,
) -> Path | None:

    ruta = Path(
        ruta_destino,
    )

    ruta.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    documento = _crear_documento(
        cotizacion,
        detalles,
        nombre_cliente,
    )

    impresora = QPrinter(
        QPrinter.PrinterMode.HighResolution,
    )

    _configurar_impresora(
        cotizacion,
        impresora,
        str(ruta),
    )

    documento.print_(
        impresora,
    )

    if not ruta.is_file():

        if parent is not None:

            QMessageBox.warning(
                parent,
                "PDF",
                "No se pudo generar el archivo PDF.",
            )

        return None

    return ruta


def exportar_pdf_cotizacion(
    cotizacion,
    detalles,
    nombre_cliente: str,
    parent: QWidget | None = None,
    *,
    cliente=None,
) -> bool:

    from aplicacion.framework.reportes.impresion_util import (
        exportar_pdf_dialogo,
    )
    from aplicacion.reportes.ventas.cotizacion import (
        crear_reporte_cotizacion,
    )

    return exportar_pdf_dialogo(
        crear_reporte_cotizacion(
            cotizacion,
            detalles,
            nombre_cliente,
            cliente=cliente,
        ),
        parent=parent,
    )


def _telefono_whatsapp(
    cliente,
) -> str:

    if cliente is None:

        return ""

    telefono = (
        getattr(
            cliente,
            "celular",
            "",
        )
        or getattr(
            cliente,
            "telefono",
            "",
        )
        or ""
    )

    digitos = "".join(
        caracter
        for caracter in str(
            telefono,
        )
        if caracter.isdigit()
    )

    if len(
        digitos,
    ) == 10:

        digitos = f"57{digitos}"

    return digitos


def enviar_whatsapp_cotizacion(
    cotizacion,
    detalles,
    nombre_cliente: str,
    cliente=None,
    parent: QWidget | None = None,
) -> bool:

    mensaje = _texto_resumen_cotizacion(
        cotizacion,
        detalles,
        nombre_cliente,
    )

    telefono = _telefono_whatsapp(
        cliente,
    )

    if telefono:

        url = (
            "https://wa.me/"
            f"{telefono}?text={quote(mensaje)}"
        )

    else:

        url = (
            "https://wa.me/?text="
            f"{quote(mensaje)}"
        )

    if not QDesktopServices.openUrl(
        QUrl(
            url,
        ),
    ):

        if parent is not None:

            QMessageBox.warning(
                parent,
                "WhatsApp",
                "No se pudo abrir WhatsApp. "
                "Verifique que tenga un navegador predeterminado.",
            )

        return False

    return True


def _correo_cliente(
    cliente,
) -> str:

    if cliente is None:

        return ""

    return str(
        getattr(
            cliente,
            "correo",
            "",
        )
        or "",
    ).strip()


def enviar_correo_cotizacion(
    cotizacion,
    detalles,
    nombre_cliente: str,
    cliente=None,
    parent: QWidget | None = None,
) -> bool:

    carpeta = _ruta_reportes()

    ruta_pdf = carpeta / nombre_archivo_pdf_cotizacion(
        cotizacion,
        nombre_cliente,
    )

    pdf = generar_pdf_cotizacion(
        cotizacion,
        detalles,
        nombre_cliente,
        ruta_pdf,
        parent=parent,
    )

    if pdf is None:

        return False

    correo = _correo_cliente(
        cliente,
    )

    asunto = quote(
        f"Cotización {cotizacion.numero}",
    )

    cuerpo = quote(
        _texto_resumen_cotizacion(
            cotizacion,
            detalles,
            nombre_cliente,
        )
        + "\n\n"
        + f"Adjunto: {pdf.name}",
    )

    destino = correo or ""

    url = (
        f"mailto:{destino}"
        f"?subject={asunto}"
        f"&body={cuerpo}"
    )

    if not QDesktopServices.openUrl(
        QUrl(
            url,
        ),
    ):

        if parent is not None:

            QMessageBox.warning(
                parent,
                "Correo",
                "No se pudo abrir el cliente de correo.",
            )

        return False

    QMessageBox.information(
        parent,
        "Correo",
        "Se generó el PDF y se abrió su cliente de correo.\n"
        f"Adjunte el archivo:\n{pdf}",
    )

    return True


def imprimir_cotizacion(
    cotizacion,
    detalles,
    nombre_cliente: str,
    parent: QWidget | None = None,
    *,
    vista_previa: bool = True,
    cliente=None,
) -> bool:

    from aplicacion.framework.reportes.impresion_util import (
        abrir_centro_impresion,
    )
    from aplicacion.reportes.ventas.cotizacion import (
        crear_reporte_cotizacion,
    )

    abrir_centro_impresion(
        crear_reporte_cotizacion(
            cotizacion,
            detalles,
            nombre_cliente,
            cliente=cliente,
        ),
        parent=parent,
        titulo=(
            f"Centro de impresión — "
            f"Cotización {cotizacion.numero}"
        ),
    )

    return True
