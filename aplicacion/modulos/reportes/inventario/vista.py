from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QPushButton,
)

from aplicacion.framework.ui.inquiry_page import InquiryPage
from aplicacion.interfaz.kpis_inicio import (
    formatear_moneda,
)
from aplicacion.modulos.inventario.bodegas.servicios import (
    ServicioBodega,
)
from aplicacion.modulos.reportes.servicios import (
    ServicioReportes,
)
from aplicacion.modulos.reportes.utilidades import (
    llenar_tabla_reporte,
)


class ReporteInventarioPage(InquiryPage):

    titulo = "Existencias de inventario"

    _NOMBRE_EXPORT = "existencias_inventario"

    def _crear_filtros(self) -> None:

        self._layout_filtros.addWidget(
            QLabel("Bodega:"),
        )

        self.bodega = QComboBox()

        self.bodega.addItem(
            "Todas (total global)",
            None,
        )

        for bodega in ServicioBodega.listar_activas():

            self.bodega.addItem(
                f"{bodega.codigo} - {bodega.nombre}",
                bodega.id,
            )

        self._layout_filtros.addWidget(
            self.bodega,
        )

        self.solo_stock = QCheckBox(
            "Solo con existencia",
        )

        self._layout_filtros.addWidget(
            self.solo_stock,
        )

        self.lbl_total = QLabel()

        self._layout_filtros.addWidget(
            self.lbl_total,
        )

        self.btn_pdf = QPushButton(
            "Exportar PDF",
        )

        self.btn_pdf.clicked.connect(
            self._exportar_pdf_reporte,
        )

        self._layout_filtros.addWidget(
            self.btn_pdf,
        )

        self._filas_reporte: list[dict] = []

    def _consultar(self) -> None:

        bodega_id = self.bodega.currentData()

        filas = ServicioReportes.existencias_inventario(
            solo_con_stock=self.solo_stock.isChecked(),
            bodega_id=bodega_id,
        )

        self._filas_reporte = filas

        columnas = [
            "Código",
            "Producto",
            "Variante",
        ]

        campos = [
            "codigo",
            "producto",
            "variante",
        ]

        if bodega_id is not None:

            columnas.append(
                "Bodega",
            )

            campos.append(
                "bodega",
            )

        columnas.extend(
            [
                "Existencia",
                "Costo",
            ],
        )

        campos.extend(
            [
                "existencia",
                "costo",
            ],
        )

        indice_existencia = campos.index(
            "existencia",
        )

        llenar_tabla_reporte(
            self.tabla,
            columnas,
            filas,
            campos=campos,
            columnas_numericas={
                indice_existencia,
                indice_existencia + 1,
            },
        )

        valor = sum(
            float(
                fila["existencia"] or 0,
            )
            * float(
                fila["costo"] or 0,
            )
            for fila in filas
        )

        self.lbl_total.setText(
            "Valor inventario: "
            f"{formatear_moneda(valor)}",
        )

    def _exportar_pdf_reporte(
        self,
    ) -> None:

        if not self._filas_reporte:

            self._consultar()

        from aplicacion.framework.reportes.impresion_util import (
            abrir_centro_impresion,
        )
        from aplicacion.framework.reportes.reporte_tabla import (
            crear_reporte_tabla,
        )

        bodega = self.bodega.currentText()

        filas_pdf = []

        for fila in self._filas_reporte:

            filas_pdf.append(
                [
                    str(
                        fila.get(
                            "codigo",
                            "",
                        ),
                    ),
                    str(
                        fila.get(
                            "producto",
                            "",
                        ),
                    ),
                    str(
                        fila.get(
                            "variante",
                            "",
                        ),
                    ),
                    f"{float(fila.get('existencia', 0) or 0):,.2f}",
                    f"{float(fila.get('costo', 0) or 0):,.2f}",
                ],
            )

        reporte = crear_reporte_tabla(
            titulo="Existencias de inventario",
            numero=bodega,
            subtitulo=(
                "Solo con stock"
                if self.solo_stock.isChecked()
                else "Todos los productos"
            ),
            columnas=[
                "Código",
                "Producto",
                "Variante",
                "Existencia",
                "Costo",
            ],
            filas=filas_pdf,
            nombre_pdf="Existencias inventario.pdf",
        )

        abrir_centro_impresion(
            reporte,
            parent=self,
        )
