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
    AZUL_NEXUS,
    BLANCO,
    GRIS_BORDE,
    GRIS_CLARO,
    estilos_reportlab,
)


class ComprobanteContablePDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        comprobante: dict,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.comprobante = comprobante
        self.estilos = estilos_reportlab()

    def armar(
        self,
    ) -> None:

        comprobante = self.comprobante
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
                    f"<b>COMPROBANTE CONTABLE {comprobante['numero']}</b>",
                    self.estilos["subtitulo"],
                ),
                Paragraph(
                    f"Fecha: {comprobante.get('fecha', '')}",
                    self.estilos["normal"],
                ),
                Spacer(
                    1,
                    3 * mm,
                ),
            ],
        )

        if comprobante.get(
            "origen",
        ):

            self.story.append(
                Paragraph(
                    f"<b>Origen:</b> {comprobante['origen']}",
                    self.estilos["normal"],
                ),
            )

        if comprobante.get(
            "descripcion",
        ):

            self.story.append(
                Paragraph(
                    f"<b>Descripción:</b> {comprobante['descripcion']}",
                    self.estilos["normal"],
                ),
            )

        self.story.extend(
            [
                Spacer(
                    1,
                    4 * mm,
                ),
                self._tabla_lineas(),
                Spacer(
                    1,
                    4 * mm,
                ),
                Paragraph(
                    (
                        f"<b>Total débito:</b> "
                        f"{dinero(comprobante.get('total_debito'))} · "
                        f"<b>Total crédito:</b> "
                        f"{dinero(comprobante.get('total_credito'))}"
                    ),
                    self.estilos["derecha_bold"],
                ),
            ],
        )

    def _tabla_lineas(
        self,
    ) -> Table:

        encabezado = [
            "#",
            "Código",
            "Cuenta",
            "Débito",
            "Crédito",
            "Detalle",
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

        for linea in self.comprobante.get(
            "lineas",
            [],
        ):

            datos.append(
                [
                    Paragraph(
                        str(
                            linea.get(
                                "numero",
                                "",
                            ),
                        ),
                        self.estilos[
                            "pequeno"
                        ],
                    ),
                    Paragraph(
                        str(
                            linea.get(
                                "codigo",
                                "",
                            ),
                        ),
                        self.estilos[
                            "pequeno"
                        ],
                    ),
                    Paragraph(
                        str(
                            linea.get(
                                "cuenta",
                                "",
                            ),
                        ),
                        self.estilos[
                            "pequeno"
                        ],
                    ),
                    Paragraph(
                        dinero(
                            linea.get(
                                "debito",
                            ),
                        ),
                        self.estilos[
                            "pequeno"
                        ],
                    ),
                    Paragraph(
                        dinero(
                            linea.get(
                                "credito",
                            ),
                        ),
                        self.estilos[
                            "pequeno"
                        ],
                    ),
                    Paragraph(
                        str(
                            linea.get(
                                "detalle",
                                "",
                            ),
                        ),
                        self.estilos[
                            "pequeno"
                        ],
                    ),
                ],
            )

        tabla = Table(
            datos,
            colWidths=[
                8 * mm,
                18 * mm,
                45 * mm,
                24 * mm,
                24 * mm,
                56 * mm,
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

        return tabla
