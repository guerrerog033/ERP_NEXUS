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


class MovimientoInventarioPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        documento: dict,
        *,
        titulo: str,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.documento = documento
        self.titulo = titulo
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
                    f"<b>{self.titulo} {doc['numero']}</b>",
                    self.estilos["subtitulo"],
                ),
                Paragraph(
                    f"Fecha: {doc.get('fecha', '')}",
                    self.estilos["normal"],
                ),
                Paragraph(
                    f"Bodega: {doc.get('bodega', '')}",
                    self.estilos["normal"],
                ),
            ],
        )

        if doc.get(
            "tipo_ajuste",
        ):

            self.story.append(
                Paragraph(
                    f"Tipo de ajuste: {doc['tipo_ajuste']}",
                    self.estilos["normal"],
                ),
            )

        if doc.get(
            "referencia",
        ):

            self.story.append(
                Paragraph(
                    f"Referencia: {doc['referencia']}",
                    self.estilos["normal"],
                ),
            )

        self.story.append(
            Spacer(
                1,
                5 * mm,
            ),
        )

        encabezado = [
            "#",
            "CÓDIGO",
            "DESCRIPCIÓN",
            "CANT.",
            "UND",
            "COSTO",
            "TOTAL",
        ]

        datos = [
            [
                Paragraph(
                    col,
                    self.estilos["normal"],
                )
                for col in encabezado
            ],
        ]

        for fila in doc.get(
            "items",
            [],
        ):

            datos.append(
                [
                    Paragraph(
                        str(
                            fila.get(
                                "numero",
                                "",
                            ),
                        ),
                        self.estilos[
                            "centro"
                        ],
                    ),
                    Paragraph(
                        str(
                            fila.get(
                                "codigo",
                                "",
                            ),
                        ),
                        self.estilos[
                            "centro"
                        ],
                    ),
                    Paragraph(
                        str(
                            fila.get(
                                "descripcion",
                                "",
                            ),
                        ),
                        self.estilos[
                            "normal"
                        ],
                    ),
                    Paragraph(
                        str(
                            fila.get(
                                "cantidad",
                                "",
                            ),
                        ),
                        self.estilos[
                            "centro"
                        ],
                    ),
                    Paragraph(
                        str(
                            fila.get(
                                "unidad",
                                "UND",
                            ),
                        ),
                        self.estilos[
                            "centro"
                        ],
                    ),
                    Paragraph(
                        dinero(
                            fila.get(
                                "costo",
                            ),
                        ),
                        self.estilos[
                            "derecha"
                        ],
                    ),
                    Paragraph(
                        dinero(
                            fila.get(
                                "total",
                            ),
                        ),
                        self.estilos[
                            "derecha_bold"
                        ],
                    ),
                ],
            )

        tabla = Table(
            datos,
            colWidths=[
                8 * mm,
                18 * mm,
                58 * mm,
                14 * mm,
                12 * mm,
                22 * mm,
                24 * mm,
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
                        self.estilos[
                            "subtitulo"
                        ],
                    ),
                    Paragraph(
                        observaciones,
                        self.estilos[
                            "normal"
                        ],
                    ),
                ],
            )
