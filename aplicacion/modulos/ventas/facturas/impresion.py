from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QWidget,
)

from aplicacion.framework.reportes.centro_impresion import (
    CentroImpresionDialog,
)
from aplicacion.framework.reportes.documento_pdf import (
    DocumentoPdf,
)
from aplicacion.modulos.ventas.facturas.formatos_impresion import (
    crear_reporte_factura_venta,
    normalizar_formato_codigo,
)


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


def nombre_archivo_pdf_factura(
    factura,
    nombre_cliente: str,
) -> str:

    numero = str(
        getattr(
            factura,
            "numero",
            "",
        )
        or "",
    ).strip()

    cliente = _sanitizar_nombre_archivo(
        nombre_cliente,
    )

    titulo = f"Factura No. {numero}"

    if cliente:

        return f"{titulo} {cliente}.pdf"

    return f"{titulo}.pdf"


def _documento_pdf_factura(
    factura,
    detalles,
    nombre_cliente: str,
    *,
    formato: str | None = None,
) -> DocumentoPdf:

    codigo = normalizar_formato_codigo(
        formato
        or getattr(
            factura,
            "formato_impresion",
            None,
        ),
    )

    reporte = crear_reporte_factura_venta(
        factura,
        detalles,
        nombre_cliente,
        formato=codigo,
    )

    return DocumentoPdf(
        reporte,
    )


def abrir_centro_impresion_factura(
    factura,
    detalles,
    nombre_cliente: str,
    *,
    parent: QWidget | None = None,
    formato: str | None = None,
) -> None:

    documento = _documento_pdf_factura(
        factura,
        detalles,
        nombre_cliente,
        formato=formato,
    )

    dialogo = CentroImpresionDialog(
        documento,
        parent=parent,
        titulo=(
            f"Centro de impresión — "
            f"Factura {documento.reporte.numero_documento}"
        ),
    )

    dialogo.exec()


def imprimir_factura_venta(
    factura,
    detalles,
    nombre_cliente: str,
    parent: QWidget | None = None,
    *,
    formato: str | None = None,
) -> bool:

    abrir_centro_impresion_factura(
        factura,
        detalles,
        nombre_cliente,
        parent=parent,
        formato=formato,
    )

    return True


def exportar_pdf_factura_venta(
    factura,
    detalles,
    nombre_cliente: str,
    parent: QWidget | None = None,
    *,
    formato: str | None = None,
) -> bool:

    documento = _documento_pdf_factura(
        factura,
        detalles,
        nombre_cliente,
        formato=formato,
    )

    ruta, _filtro = QFileDialog.getSaveFileName(
        parent,
        "Exportar factura en PDF",
        documento.reporte.nombre_archivo_pdf(),
        "PDF (*.pdf)",
    )

    if not ruta:

        return False

    if not ruta.lower().endswith(
        ".pdf",
    ):

        ruta = f"{ruta}.pdf"

    documento.exportar_pdf(
        ruta,
    )

    if not Path(
        ruta,
    ).is_file():

        QMessageBox.warning(
            parent,
            "PDF",
            "No se pudo generar el archivo PDF.",
        )

        return False

    QMessageBox.information(
        parent,
        "PDF",
        f"Archivo guardado en:\n{ruta}",
    )

    return True
