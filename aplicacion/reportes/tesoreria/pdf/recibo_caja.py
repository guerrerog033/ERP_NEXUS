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


class ReciboCajaPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        recibo: dict,
        **kwargs,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.recibo = recibo
        self.estilos = estilos_reportlab()

    def armar(
        self,
    ) -> None:

        recibo = self.recibo

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
                titulo_documento="RECIBO DE CAJA",
                numero=str(
                    recibo.get(
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
                        recibo.get(
                            "fecha",
                            "",
                        ),
                    ),
                    (
                        "Forma de pago",
                        recibo.get(
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
                recibo[
                    "cliente"
                ],
                titulo="RECIBIMOS DE",
                estilos=self.estilos,
            ),
        )

        self.story.append(
            Spacer(
                1,
                4 * mm,
            ),
        )

        lineas = recibo.get(
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
                    f"<b>VALOR RECIBIDO:</b> {dinero(recibo.get('valor'))}",
                    self.estilos["derecha_bold"],
                ),
                Paragraph(
                    f"<b>SON:</b> {recibo.get('total_letras', '')}",
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
                recibo.get(
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
                    18 * mm,
                ),
                Paragraph(
                    "______________________________",
                    self.estilos["centro"],
                ),
                Paragraph(
                    "Responsable",
                    self.estilos["centro"],
                ),
            ],
        )
