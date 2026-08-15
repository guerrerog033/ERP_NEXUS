from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import Spacer

from aplicacion.framework.reportes.pdf.documento_base import (
    DocumentoReportLab,
)
from aplicacion.framework.reportes.pdf.estilos import (
    estilos_reportlab,
)


class NotaVentaPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        nota: dict,
        *,
        titulo: str = "NOTA",
        electronica: bool = False,
        **kwargs,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.nota = nota
        self.titulo = titulo
        self.electronica = electronica
        self.estilos = estilos_reportlab()

    def armar(
        self,
    ) -> None:

        self._encabezado()
        self._meta()
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
                    self.nota.get(
                        "numero",
                        "",
                    )
                    or "",
                ),
                estilos=self.estilos,
            ),
        )

    def _meta(
        self,
    ) -> None:

        from aplicacion.documentos.impresion.componentes import (
            construir_meta_documento,
        )

        nota = self.nota

        self.story.extend(
            construir_meta_documento(
                [
                    (
                        "Fecha",
                        nota.get(
                            "fecha_generacion",
                            nota.get(
                                "fecha",
                                "",
                            ),
                        ),
                    ),
                    (
                        "Factura referencia",
                        nota.get(
                            "factura_referencia",
                            "",
                        ),
                    ),
                    (
                        "Motivo",
                        nota.get(
                            "motivo",
                            "",
                        ),
                    ),
                    (
                        "CUFE factura",
                        nota.get(
                            "factura_cufe",
                            "",
                        ),
                    ),
                ],
                estilos=self.estilos,
            ),
        )

    def _cliente(
        self,
    ) -> None:

        from aplicacion.documentos.impresion.componentes import (
            construir_bloque_tercero,
        )

        self.story.append(
            construir_bloque_tercero(
                self.nota[
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

        from aplicacion.documentos.impresion.componentes import (
            construir_tabla_detalle,
        )

        self.story.extend(
            [
                construir_tabla_detalle(
                    self.nota[
                        "items"
                    ],
                    estilos=self.estilos,
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

        from aplicacion.documentos.impresion.componentes import (
            construir_bloque_totales,
        )

        nota = self.nota

        self.story.extend(
            construir_bloque_totales(
                nota[
                    "subtotal"
                ],
                nota[
                    "descuento"
                ],
                nota[
                    "impuestos"
                ],
                nota[
                    "total"
                ],
                total_letras=nota.get(
                    "total_letras",
                    "",
                ),
                estilos=self.estilos,
            ),
        )

        self.story.append(
            Spacer(
                1,
                4 * mm,
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
                self.nota,
                estilos=self.estilos,
            ),
        )

    def _observaciones(
        self,
    ) -> None:

        from aplicacion.documentos.impresion.componentes import (
            construir_observaciones,
        )

        self.story.extend(
            construir_observaciones(
                self.nota.get(
                    "observaciones",
                    "",
                ),
                estilos=self.estilos,
            ),
        )
