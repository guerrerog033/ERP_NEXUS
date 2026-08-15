from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.platypus import Spacer

from aplicacion.framework.reportes.pdf.documento_base import (
    DocumentoReportLab,
)
from aplicacion.framework.reportes.pdf.estilos import (
    estilos_reportlab,
)


class RemisionPDF(
    DocumentoReportLab,
):

    def __init__(
        self,
        archivo,
        empresa: dict,
        remision: dict,
        *,
        titulo: str = "REMISIÓN",
        electronica: bool = False,
        codigo_label: str = "CUFE",
        **kwargs,
    ):

        super().__init__(
            archivo,
            empresa,
        )

        self.remision = remision
        self.titulo = titulo
        self.electronica = electronica
        self.codigo_label = codigo_label
        self.estilos = estilos_reportlab()

    def armar(
        self,
    ) -> None:

        self._encabezado()
        self._meta()
        self._cliente()
        self._detalle()
        self._observaciones()

        if self.electronica:

            self._informacion_electronica()

        self._firmas()

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
                    self.remision.get(
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

        remision = self.remision
        cliente = remision.get(
            "cliente",
            {},
        )

        self.story.extend(
            construir_meta_documento(
                [
                    (
                        "Fecha",
                        remision.get(
                            "fecha",
                            "",
                        ),
                    ),
                    (
                        "Estado",
                        remision.get(
                            "estado",
                            "",
                        ),
                    ),
                    (
                        "Vendedor",
                        remision.get(
                            "vendedor",
                            "",
                        ),
                    ),
                    (
                        "Pedido",
                        remision.get(
                            "pedido_numero",
                            "",
                        ),
                    ),
                    (
                        "Dirección entrega",
                        remision.get(
                            "direccion_entrega",
                            cliente.get(
                                "direccion",
                                "",
                            ),
                        ),
                    ),
                    (
                        "Transportador",
                        remision.get(
                            "transportador",
                            "",
                        ),
                    ),
                    (
                        "Vehículo",
                        remision.get(
                            "vehiculo",
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
                self.remision[
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
            construir_tabla_logistica,
        )

        self.story.extend(
            [
                construir_tabla_logistica(
                    self.remision[
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

    def _observaciones(
        self,
    ) -> None:

        from aplicacion.documentos.impresion.componentes import (
            construir_observaciones,
        )

        self.story.extend(
            construir_observaciones(
                self.remision.get(
                    "observaciones",
                    "",
                ),
                estilos=self.estilos,
            ),
        )

    def _informacion_electronica(
        self,
    ) -> None:

        from aplicacion.documentos.impresion.componentes import (
            construir_pie_electronico,
        )

        payload = {
            **self.remision,
            "cufe": self.remision.get(
                "cufe",
                "",
            )
            or self.remision.get(
                "cude",
                "",
            ),
        }

        self.story.extend(
            construir_pie_electronico(
                payload,
                estilos=self.estilos,
            ),
        )

    def _firmas(
        self,
    ) -> None:

        from aplicacion.documentos.impresion.componentes import (
            construir_bloque_firmas,
        )

        remision = self.remision

        self.story.extend(
            construir_bloque_firmas(
                transportador=str(
                    remision.get(
                        "transportador",
                        "",
                    )
                    or "",
                ),
                vehiculo=str(
                    remision.get(
                        "vehiculo",
                        "",
                    )
                    or "",
                ),
                estilos=self.estilos,
            ),
        )
