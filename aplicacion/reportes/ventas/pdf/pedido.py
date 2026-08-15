from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import Spacer

from aplicacion.framework.reportes.pdf.documento_base import (
    DocumentoReportLab,
)
from aplicacion.framework.reportes.pdf.estilos import (
    estilos_reportlab,
)


class PedidoVentaPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        pedido: dict,
        **kwargs,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.pedido = pedido
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
                titulo_documento="PEDIDO DE VENTA",
                numero=str(
                    self.pedido.get(
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

        pedido = self.pedido

        self.story.extend(
            construir_meta_documento(
                [
                    (
                        "Fecha",
                        pedido.get(
                            "fecha",
                            "",
                        ),
                    ),
                    (
                        "Estado",
                        pedido.get(
                            "estado",
                            "",
                        ),
                    ),
                    (
                        "Vendedor",
                        pedido.get(
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
                self.pedido[
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
                    self.pedido[
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

        pedido = self.pedido

        self.story.extend(
            construir_bloque_totales(
                pedido[
                    "subtotal"
                ],
                pedido[
                    "descuento"
                ],
                pedido[
                    "impuestos"
                ],
                pedido[
                    "total"
                ],
                total_letras=pedido.get(
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
                self.pedido.get(
                    "observaciones",
                    "",
                ),
                estilos=self.estilos,
            ),
        )
