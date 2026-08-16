from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import QComboBox, QLabel

from aplicacion.framework.ui.inquiry_page import InquiryPage
from aplicacion.modulos.reportes.exogena.servicio import (
    ServicioInformacionExogena,
)
from aplicacion.modulos.reportes.utilidades import (
    llenar_tabla_reporte,
)

_FORMATOS: dict[str, str] = {
    "Pagos a terceros y retenciones practicadas": "pagos_y_retenciones",
    "Retenciones que le practicaron": "retenciones_que_le_practicaron",
    "Ingresos recibidos": "ingresos_recibidos",
}

_COLUMNAS = [
    "Tipo doc.",
    "Número",
    "DV",
    "Nombre / Razón social",
    "Valor base",
    "IVA",
    "Retefuente",
    "ReteICA",
    "ReteIVA",
    "Total",
]

_CAMPOS = [
    "tipo_documento",
    "numero_documento",
    "dv",
    "nombre",
    "valor_base",
    "valor_iva",
    "valor_retefuente",
    "valor_reteica",
    "valor_reteiva",
    "valor_total",
]

_NUMERICAS = {4, 5, 6, 7, 8, 9}


class InformacionExogenaPage(InquiryPage):
    """
    Totales anuales por tercero para diligenciar el reporte de
    información exógena DIAN (formatos 1001/1003/1007) en el
    prevalidador tributario oficial. No genera el archivo plano de
    envío a la DIAN.
    """

    titulo = "Información exógena"

    _COLUMNAS = _COLUMNAS
    _NOMBRE_EXPORT = "informacion_exogena"
    _TITULO_BOTON = "Consultar"

    def _crear_filtros(self) -> None:

        self._layout_filtros.addWidget(
            QLabel("Año:"),
        )

        self.combo_anio = QComboBox()

        anio_actual = date.today().year

        for anio in range(
            anio_actual,
            anio_actual - 6,
            -1,
        ):

            self.combo_anio.addItem(
                str(anio),
                anio,
            )

        self._layout_filtros.addWidget(
            self.combo_anio,
        )

        self._layout_filtros.addWidget(
            QLabel("Formato:"),
        )

        self.combo_formato = QComboBox()

        for etiqueta in _FORMATOS:

            self.combo_formato.addItem(
                etiqueta,
            )

        self._layout_filtros.addWidget(
            self.combo_formato,
        )

    def _consultar(self) -> None:

        anio = self.combo_anio.currentData()

        metodo_nombre = _FORMATOS[
            self.combo_formato.currentText()
        ]

        metodo = getattr(
            ServicioInformacionExogena,
            metodo_nombre,
        )

        filas = metodo(anio)

        llenar_tabla_reporte(
            self.tabla,
            _COLUMNAS,
            filas,
            campos=_CAMPOS,
            columnas_numericas=_NUMERICAS,
        )
