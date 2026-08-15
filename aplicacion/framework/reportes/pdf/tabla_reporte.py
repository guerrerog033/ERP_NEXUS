from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .documento_base import DocumentoReportLab
from .estilos import (
    AZUL_CLARO,
    AZUL_NEXUS,
    BLANCO,
    GRIS_BORDE,
    GRIS_CLARO,
    estilos_reportlab,
)


class TablaReportePDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        documento: dict,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.documento = documento
        self.estilos = estilos_reportlab()

    def armar(
        self,
    ) -> None:

        doc = self.documento
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
                    f"<b>{doc.get('titulo', 'REPORTE')}</b>",
                    self.estilos["subtitulo"],
                ),
                Paragraph(
                    doc.get(
                        "numero",
                        "",
                    ),
                    self.estilos["normal"],
                ),
            ],
        )

        if doc.get(
            "subtitulo",
        ):

            self.story.append(
                Paragraph(
                    doc[
                        "subtitulo"
                    ],
                    self.estilos["pequeno"],
                ),
            )

        self.story.append(
            Spacer(
                1,
                5 * mm,
            ),
        )

        columnas = doc.get(
            "columnas",
            [],
        )

        filas = doc.get(
            "filas",
            [],
        )

        if not columnas:

            return

        datos = [
            [
                Paragraph(
                    str(
                        col,
                    ),
                    self.estilos["normal"],
                )
                for col in columnas
            ],
        ]

        for fila in filas:

            datos.append(
                [
                    Paragraph(
                        str(
                            valor,
                        ),
                        self.estilos[
                            "pequeno"
                        ],
                    )
                    for valor in fila
                ],
            )

        ancho_total = (
            175 * mm
        )

        ancho_col = ancho_total / max(
            len(
                columnas,
            ),
            1,
        )

        tabla = Table(
            datos,
            colWidths=[
                ancho_col
            ]
            * len(
                columnas,
            ),
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
                        0.35,
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
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ],
            ),
        )

        self.story.append(
            tabla,
        )

        if doc.get(
            "pie",
        ):

            self.story.extend(
                [
                    Spacer(
                        1,
                        4 * mm,
                    ),
                    Paragraph(
                        str(
                            doc[
                                "pie"
                            ],
                        ),
                        self.estilos[
                            "pequeno"
                        ],
                    ),
                ],
            )
