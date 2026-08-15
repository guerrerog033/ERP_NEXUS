from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from aplicacion.framework.reportes.pdf.componentes import (
    bloque_totales,
    tabla_detalle,
)
from aplicacion.framework.reportes.pdf.documento_base import (
    DocumentoReportLab,
)
from aplicacion.framework.reportes.pdf.estilos import (
    AZUL_CLARO,
    GRIS_BORDE,
    estilos_reportlab,
)


class FacturaCompraPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        factura: dict,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.factura = factura
        self.estilos = estilos_reportlab()

    def armar(
        self,
    ) -> None:

        self._encabezado()
        self._proveedor()
        self._detalle()
        self._totales()
        self._info_adicional()
        self._observaciones()

    def _encabezado(
        self,
    ) -> None:

        empresa = self.empresa
        factura = self.factura

        izquierdo = [
            Paragraph(
                f"<b>{empresa.get('razon_social') or empresa.get('nombre', '')}</b>",
                self.estilos["titulo"],
            ),
            Paragraph(
                f"NIT: {empresa.get('nit', '')}",
                self.estilos["normal"],
            ),
            Paragraph(
                empresa.get(
                    "direccion",
                    "",
                ),
                self.estilos["normal"],
            ),
        ]

        derecho = [
            Paragraph(
                factura.get(
                    "titulo_documento",
                    "FACTURA DE COMPRA",
                ),
                self.estilos["subtitulo"],
            ),
            Spacer(
                1,
                2 * mm,
            ),
            Paragraph(
                f"<b>{factura['numero']}</b>",
                self.estilos["titulo"],
            ),
            Paragraph(
                f"Fecha: {factura.get('fecha', '')}",
                self.estilos["normal"],
            ),
        ]

        if factura.get(
            "estado",
        ):

            derecho.append(
                Paragraph(
                    f"Estado: {factura['estado']}",
                    self.estilos["pequeno"],
                ),
            )

        tabla = Table(
            [
                [
                    izquierdo,
                    derecho,
                ],
            ],
            colWidths=[
                100 * mm,
                75 * mm,
            ],
        )

        tabla.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.8,
                        GRIS_BORDE,
                    ),
                    (
                        "BACKGROUND",
                        (1, 0),
                        (1, 0),
                        AZUL_CLARO,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                ],
            ),
        )

        self.story.extend(
            [
                tabla,
                Spacer(
                    1,
                    5 * mm,
                ),
            ],
        )

    def _proveedor(
        self,
    ) -> None:

        proveedor = self.factura[
            "proveedor"
        ]

        datos = [
            [
                Paragraph(
                    "<b>PROVEEDOR</b>",
                    self.estilos["subtitulo"],
                ),
                "",
            ],
            [
                Paragraph(
                    f"<b>{proveedor['nombre']}</b>",
                    self.estilos["normal"],
                ),
                Paragraph(
                    f"NIT / DOCUMENTO: {proveedor.get('documento', '')}",
                    self.estilos["normal"],
                ),
            ],
            [
                Paragraph(
                    f"DIRECCIÓN: {proveedor.get('direccion', '')}",
                    self.estilos["normal"],
                ),
                Paragraph(
                    f"CIUDAD: {proveedor.get('ciudad', '')}",
                    self.estilos["normal"],
                ),
            ],
        ]

        tabla = Table(
            datos,
            colWidths=[
                90 * mm,
                85 * mm,
            ],
        )

        tabla.setStyle(
            TableStyle(
                [
                    (
                        "SPAN",
                        (0, 0),
                        (-1, 0),
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        AZUL_CLARO,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        GRIS_BORDE,
                    ),
                    (
                        "GRID",
                        (0, 1),
                        (-1, -1),
                        0.3,
                        GRIS_BORDE,
                    ),
                ],
            ),
        )

        self.story.extend(
            [
                tabla,
                Spacer(
                    1,
                    5 * mm,
                ),
            ],
        )

    def _detalle(
        self,
    ) -> None:

        self.story.extend(
            [
                tabla_detalle(
                    self.factura[
                        "items"
                    ],
                    self.estilos,
                ),
                Spacer(
                    1,
                    4 * mm,
                ),
            ],
        )

    def _totales(
        self,
    ) -> None:

        factura = self.factura

        self.story.append(
            bloque_totales(
                factura[
                    "subtotal"
                ],
                factura[
                    "descuento"
                ],
                factura[
                    "impuestos"
                ],
                factura[
                    "total"
                ],
                self.estilos,
            ),
        )

        self.story.append(
            Spacer(
                1,
                4 * mm,
            ),
        )

        self.story.append(
            Paragraph(
                f"<b>SON:</b> {factura.get('total_letras', '')}",
                self.estilos["normal"],
            ),
        )

    def _info_adicional(
        self,
    ) -> None:

        lineas = self.factura.get(
            "info_adicional",
            [],
        )

        if not lineas:

            return

        self.story.extend(
            [
                Spacer(
                    1,
                    4 * mm,
                ),
                Paragraph(
                    "<b>INFORMACIÓN ADICIONAL</b>",
                    self.estilos["subtitulo"],
                ),
            ],
        )

        for linea in lineas:

            self.story.append(
                Paragraph(
                    str(
                        linea,
                    ),
                    self.estilos["pequeno"],
                ),
            )

    def _observaciones(
        self,
    ) -> None:

        observaciones = self.factura.get(
            "observaciones",
            "",
        )

        if not observaciones:

            return

        self.story.extend(
            [
                Spacer(
                    1,
                    5 * mm,
                ),
                Paragraph(
                    "<b>OBSERVACIONES</b>",
                    self.estilos["subtitulo"],
                ),
                Paragraph(
                    observaciones,
                    self.estilos["normal"],
                ),
            ],
        )
