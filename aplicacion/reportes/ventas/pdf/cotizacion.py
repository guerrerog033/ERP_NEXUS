from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import Spacer

from aplicacion.framework.reportes.pdf.documento_base import (
    DocumentoReportLab,
)
from aplicacion.framework.reportes.pdf.estilos import (
    estilos_reportlab,
)


class CotizacionPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        cotizacion: dict,
        **kwargs,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.cotizacion = cotizacion
        self.estilos = estilos_reportlab()

    def armar(
        self,
    ) -> None:

        self._encabezado()
        self._meta()
        self._cliente()
        self._detalle()
        self._totales()
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
                titulo_documento="COTIZACIÓN",
                numero=str(
                    self.cotizacion.get(
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

        cotizacion = self.cotizacion

        self.story.extend(
            construir_meta_documento(
                [
                    (
                        "Fecha",
                        cotizacion.get(
                            "fecha",
                            "",
                        ),
                    ),
                    (
                        "Vigencia",
                        cotizacion.get(
                            "fecha_vigencia",
                            "",
                        ),
                    ),
                    (
                        "Vendedor",
                        cotizacion.get(
                            "vendedor",
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
                self.cotizacion[
                    "cliente"
                ],
                titulo="CLIENTE",
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
                    self.cotizacion[
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

        cotizacion = self.cotizacion

        self.story.extend(
            construir_bloque_totales(
                cotizacion[
                    "subtotal"
                ],
                cotizacion[
                    "descuento"
                ],
                cotizacion[
                    "impuestos"
                ],
                cotizacion[
                    "total"
                ],
                total_letras=cotizacion.get(
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

    def _observaciones(
        self,
    ) -> None:

        from aplicacion.documentos.impresion.componentes import (
            construir_observaciones,
        )

        self.story.extend(
            construir_observaciones(
                self.cotizacion.get(
                    "observaciones",
                    "",
                ),
                estilos=self.estilos,
            ),
        )
