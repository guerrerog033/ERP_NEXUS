from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from aplicacion.framework.reportes.pdf.documento_base import (
    DocumentoReportLab,
)
from aplicacion.framework.reportes.pdf.estilos import (
    AZUL_CLARO,
    AZUL_NEXUS,
    BLANCO,
    GRIS_BORDE,
    estilos_reportlab,
)


class TrasladoInventarioPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        traslado: dict,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.traslado = traslado
        self.estilos = estilos_reportlab()

    def armar(
        self,
    ) -> None:

        doc = self.traslado
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
                    f"<b>TRASLADO {doc['numero']}</b>",
                    self.estilos["subtitulo"],
                ),
                Paragraph(
                    f"Fecha: {doc.get('fecha', '')}",
                    self.estilos["normal"],
                ),
                Paragraph(
                    f"<b>Origen:</b> {doc.get('bodega_origen', '')}",
                    self.estilos["normal"],
                ),
                Paragraph(
                    f"<b>Destino:</b> {doc.get('bodega_destino', '')}",
                    self.estilos["normal"],
                ),
                Spacer(
                    1,
                    5 * mm,
                ),
            ],
        )

        filas = [
            [
                "ITEM",
                "CÓDIGO",
                "DESCRIPCIÓN",
                "CANTIDAD",
                "UND",
            ],
        ]

        for item in doc.get(
            "items",
            [],
        ):

            filas.append(
                [
                    str(
                        item.get(
                            "numero",
                            "",
                        ),
                    ),
                    str(
                        item.get(
                            "codigo",
                            "",
                        ),
                    ),
                    str(
                        item.get(
                            "descripcion",
                            "",
                        ),
                    ),
                    str(
                        item.get(
                            "cantidad",
                            "",
                        ),
                    ),
                    str(
                        item.get(
                            "unidad",
                            "UND",
                        ),
                    ),
                ],
            )

        tabla = Table(
            filas,
            colWidths=[
                12 * mm,
                22 * mm,
                88 * mm,
                22 * mm,
                18 * mm,
            ],
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
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        AZUL_CLARO,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        GRIS_BORDE,
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER",
                    ),
                ],
            ),
        )

        self.story.append(
            tabla,
        )

        observaciones = doc.get(
            "observaciones",
            "",
        )

        if observaciones:

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
