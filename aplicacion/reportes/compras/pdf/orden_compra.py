from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from aplicacion.framework.reportes.pdf.componentes import (
    dinero,
)
from aplicacion.framework.reportes.pdf.documento_base import (
    DocumentoReportLab,
)
from aplicacion.framework.reportes.pdf.estilos import (
    AZUL_CLARO,
    AZUL_NEXUS,
    BLANCO,
    GRIS_BORDE,
    GRIS_CLARO,
    estilos_reportlab,
)


class OrdenCompraPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        orden: dict,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.orden = orden
        self.estilos = estilos_reportlab()

    def armar(
        self,
    ) -> None:

        self._encabezado()
        self._proveedor()
        self._detalle()
        self._totales()
        self._observaciones()

    def _encabezado(
        self,
    ) -> None:

        orden = self.orden
        empresa = self.empresa

        self.story.extend(
            [
                Paragraph(
                    f"<b>{empresa.get('razon_social') or empresa.get('nombre', '')}</b>",
                    self.estilos["titulo"],
                ),
                Paragraph(
                    f"NIT: {empresa.get('nit', '')}",
                    self.estilos["normal"],
                ),
                Paragraph(
                    f"<b>ORDEN DE COMPRA {orden['numero']}</b>",
                    self.estilos["subtitulo"],
                ),
                Paragraph(
                    f"Fecha: {orden.get('fecha', '')}",
                    self.estilos["normal"],
                ),
                Spacer(
                    1,
                    4 * mm,
                ),
            ],
        )

    def _proveedor(
        self,
    ) -> None:

        proveedor = self.orden[
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
                    f"Documento: {proveedor.get('documento', '')}",
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

        encabezado = [
            "#",
            "DESCRIPCIÓN",
            "CANT.",
            "RECIBIDA",
            "COSTO",
            "TOTAL",
        ]

        datos = [
            [
                Paragraph(
                    valor,
                    self.estilos["normal"],
                )
                for valor in encabezado
            ],
        ]

        for fila in self.orden[
            "items"
        ]:

            datos.append(
                [
                    Paragraph(
                        str(
                            fila.get(
                                "numero",
                                "",
                            ),
                        ),
                        self.estilos["centro"],
                    ),
                    Paragraph(
                        str(
                            fila.get(
                                "descripcion",
                                "",
                            ),
                        ),
                        self.estilos["normal"],
                    ),
                    Paragraph(
                        str(
                            fila.get(
                                "cantidad",
                                "",
                            ),
                        ),
                        self.estilos["centro"],
                    ),
                    Paragraph(
                        str(
                            fila.get(
                                "recibida",
                                "",
                            ),
                        ),
                        self.estilos["centro"],
                    ),
                    Paragraph(
                        dinero(
                            fila.get(
                                "costo",
                            ),
                        ),
                        self.estilos["derecha"],
                    ),
                    Paragraph(
                        dinero(
                            fila.get(
                                "total",
                            ),
                        ),
                        self.estilos["derecha_bold"],
                    ),
                ],
            )

        tabla = Table(
            datos,
            colWidths=[
                8 * mm,
                58 * mm,
                16 * mm,
                18 * mm,
                24 * mm,
                26 * mm,
            ],
            repeatRows=1,
        )

        tabla.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        AZUL_NEXUS,
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        BLANCO,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        GRIS_BORDE,
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            BLANCO,
                            GRIS_CLARO,
                        ],
                    ),
                ],
            ),
        )

        self.story.extend(
            [
                tabla,
                Spacer(
                    1,
                    4 * mm,
                ),
            ],
        )

    def _totales(
        self,
    ) -> None:

        orden = self.orden

        datos = [
            [
                "",
                Paragraph(
                    "SUBTOTAL",
                    self.estilos["normal"],
                ),
                Paragraph(
                    dinero(
                        orden.get(
                            "subtotal",
                        ),
                    ),
                    self.estilos["derecha"],
                ),
            ],
            [
                "",
                Paragraph(
                    "<b>TOTAL</b>",
                    self.estilos["normal"],
                ),
                Paragraph(
                    f"<b>{dinero(orden.get('total'))}</b>",
                    self.estilos["derecha_bold"],
                ),
            ],
        ]

        tabla = Table(
            datos,
            colWidths=[
                80 * mm,
                45 * mm,
                40 * mm,
            ],
        )

        tabla.setStyle(
            TableStyle(
                [
                    (
                        "LINEABOVE",
                        (1, -1),
                        (-1, -1),
                        1,
                        AZUL_NEXUS,
                    ),
                    (
                        "BACKGROUND",
                        (1, -1),
                        (-1, -1),
                        AZUL_CLARO,
                    ),
                ],
            ),
        )

        self.story.extend(
            [
                tabla,
                Spacer(
                    1,
                    4 * mm,
                ),
                Paragraph(
                    f"<b>SON:</b> {orden.get('total_letras', '')}",
                    self.estilos["normal"],
                ),
            ],
        )

    def _observaciones(
        self,
    ) -> None:

        observaciones = self.orden.get(
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
