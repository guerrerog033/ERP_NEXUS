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
    qr_imagen,
    tabla_detalle,
)
from aplicacion.framework.reportes.pdf.documento_base import (
    DocumentoReportLab,
)
from aplicacion.framework.reportes.pdf.estilos import (
    AZUL_CLARO,
    AZUL_NEXUS,
    GRIS_BORDE,
    estilos_reportlab,
)


class FacturaVentaPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        factura: dict,
        *,
        titulo: str = "FACTURA DE VENTA",
        electronica: bool = False,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.factura = factura
        self.titulo = titulo
        self.electronica = electronica
        self.estilos = estilos_reportlab()

    def armar(
        self,
    ) -> None:

        self._encabezado()
        self._datos_factura()
        self._cliente()
        self._detalle()
        self._totales()

        if self.electronica:

            self._informacion_electronica()

        self._observaciones()

    def _encabezado(
        self,
    ) -> None:

        from aplicacion.documentos.impresion.componentes import (
            construir_encabezado_empresa,
        )

        self.story.extend(
            construir_encabezado_empresa(
                self.empresa,
                titulo_documento=self.titulo,
                numero=str(
                    self.factura.get(
                        "numero",
                        "",
                    )
                    or "",
                ),
                estilos=self.estilos,
            ),
        )

    def _datos_factura(
        self,
    ) -> None:

        factura = self.factura

        datos = [
            [
                Paragraph(
                    "<b>FECHA GENERACIÓN</b>",
                    self.estilos["pequeno"],
                ),
                Paragraph(
                    "<b>FECHA VENCIMIENTO</b>",
                    self.estilos["pequeno"],
                ),
                Paragraph(
                    "<b>FORMA DE PAGO</b>",
                    self.estilos["pequeno"],
                ),
                Paragraph(
                    "<b>MEDIO DE PAGO</b>",
                    self.estilos["pequeno"],
                ),
            ],
            [
                Paragraph(
                    factura.get(
                        "fecha_generacion",
                        "",
                    ),
                    self.estilos["normal"],
                ),
                Paragraph(
                    factura.get(
                        "fecha_vencimiento",
                        "",
                    ),
                    self.estilos["normal"],
                ),
                Paragraph(
                    factura.get(
                        "forma_pago",
                        "",
                    ),
                    self.estilos["normal"],
                ),
                Paragraph(
                    factura.get(
                        "medio_pago",
                        "",
                    ),
                    self.estilos["normal"],
                ),
            ],
        ]

        tabla = Table(
            datos,
            colWidths=[
                43 * mm,
                43 * mm,
                43 * mm,
                46 * mm,
            ],
        )

        tabla.setStyle(
            TableStyle(
                [
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
                        (0, 0),
                        (-1, -1),
                        0.3,
                        GRIS_BORDE,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
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

    def _cliente(
        self,
    ) -> None:

        from aplicacion.documentos.impresion.componentes import (
            construir_bloque_tercero,
        )

        self.story.append(
            construir_bloque_tercero(
                self.factura[
                    "cliente"
                ],
                titulo="ADQUIRIENTE",
                estilos=self.estilos,
            ),
        )

        self.story.append(
            Spacer(
                1,
                4 * mm,
            ),
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

    def _informacion_electronica(
        self,
    ) -> None:

        from aplicacion.documentos.impresion.componentes import (
            construir_pie_electronico,
        )

        self.story.extend(
            construir_pie_electronico(
                self.factura,
                estilos=self.estilos,
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
