from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    Spacer,
)

from aplicacion.framework.reportes.pdf.componentes import (
    dinero,
)
from aplicacion.framework.reportes.pdf.documento_base import (
    DocumentoReportLab,
)
from aplicacion.framework.reportes.pdf.estilos import (
    estilos_reportlab,
)


class ComprobanteEgresoPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        comprobante: dict,
        **kwargs,
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

        from aplicacion.documentos.impresion.componentes import (
            construir_aplicacion_cartera,
            construir_bloque_tercero,
            construir_encabezado_empresa,
            construir_meta_documento,
            construir_observaciones,
        )

        self.story.extend(
            construir_encabezado_empresa(
                self.empresa,
                titulo_documento="COMPROBANTE DE EGRESO",
                numero=str(
                    comprobante.get(
                        "numero",
                        "",
                    )
                    or "",
                ),
                estilos=self.estilos,
            ),
        )

        self.story.extend(
            construir_meta_documento(
                [
                    (
                        "Fecha",
                        comprobante.get(
                            "fecha",
                            "",
                        ),
                    ),
                    (
                        "Forma de pago",
                        comprobante.get(
                            "forma_pago",
                            "",
                        ),
                    ),
                ],
                estilos=self.estilos,
            ),
        )

        self.story.append(
            construir_bloque_tercero(
                comprobante[
                    "beneficiario"
                ],
                titulo="PAGADO A",
                estilos=self.estilos,
            ),
        )

        self.story.append(
            Spacer(
                1,
                4 * mm,
            ),
        )

        lineas = comprobante.get(
            "lineas",
            [],
        )

        if lineas:

            self.story.extend(
                construir_aplicacion_cartera(
                    lineas,
                    estilos=self.estilos,
                ),
            )

            self.story.append(
                Spacer(
                    1,
                    4 * mm,
                ),
            )

        self.story.extend(
            [
                Paragraph(
                    f"<b>Valor:</b> {dinero(comprobante.get('valor'))}",
                    self.estilos["derecha_bold"],
                ),
                Paragraph(
                    f"<b>SON:</b> {comprobante.get('total_letras', '')}",
                    self.estilos["normal"],
                ),
                Spacer(
                    1,
                    4 * mm,
                ),
            ],
        )

        self.story.extend(
            construir_observaciones(
                comprobante.get(
                    "concepto",
                    "",
                ),
                estilos=self.estilos,
            ),
        )

        self.story.extend(
            [
                Spacer(
                    1,
                    14 * mm,
                ),
                Paragraph(
                    "ELABORÓ       REVISÓ       APROBÓ",
                    self.estilos["centro"],
                ),
                Spacer(
                    1,
                    10 * mm,
                ),
                Paragraph(
                    "__________    __________    __________",
                    self.estilos["centro"],
                ),
            ],
        )
