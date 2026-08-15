from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QMessageBox,
    QSpinBox,
    QTableWidgetItem,
)

from aplicacion.framework.ui.inquiry_page import InquiryPage
from aplicacion.interfaz.kpis_inicio import (
    formatear_moneda,
)
from aplicacion.modulos.nomina.integracion import (
    IntegracionNomina,
)
from aplicacion.modulos.nomina.servicios import (
    ServicioNomina,
)


class LiquidacionNominaPage(InquiryPage):

    titulo = "Liquidación de nómina"

    _NOMBRE_EXPORT = "liquidacion_nomina"

    _COLUMNAS = [
        "Código",
        "Empleado",
        "Documento",
        "Devengado",
        "Deducciones",
        "Neto a pagar",
        "Aportes patronales",
    ]

    def _crear_filtros(self) -> None:

        self._layout_filtros.addWidget(
            QLabel("Periodo:"),
        )

        self.periodo = QComboBox()

        self._cargar_periodos()

        self._layout_filtros.addWidget(
            self.periodo,
            1,
        )

        self._layout_filtros.addWidget(
            QLabel("Días:"),
        )

        self.dias = QSpinBox()

        self.dias.setMinimum(1)
        self.dias.setMaximum(30)
        self.dias.setValue(30)

        self._layout_filtros.addWidget(
            self.dias,
        )

        self.lbl_total = QLabel()

        self._layout_filtros.addWidget(
            self.lbl_total,
        )

    def _agregar_botones_filtro(self) -> None:

        self._layout_filtros.addWidget(
            self._crear_boton(
                "Nuevo periodo",
                self._nuevo_periodo,
            ),
        )

        self._layout_filtros.addWidget(
            self._crear_boton(
                "Liquidar",
                self._liquidar,
            ),
        )

        self._layout_filtros.addWidget(
            self._crear_boton(
                "Exportar PILA",
                self._exportar_pila,
            ),
        )

        self._layout_filtros.addWidget(
            self._crear_boton(
                "Contabilizar",
                self._contabilizar,
            ),
        )

        self._layout_filtros.addWidget(
            self._crear_boton(
                "Nómina DIAN",
                self._emitir_dian,
            ),
        )

    def _crear_boton(
        self,
        titulo: str,
        slot,
    ):

        from PySide6.QtWidgets import QPushButton

        boton = QPushButton(titulo)

        boton.clicked.connect(slot)

        return boton

    def _cargar_periodos(self) -> None:

        self.periodo.clear()

        periodos = ServicioNomina.listar_periodos()

        if not periodos:

            self.periodo.addItem(
                "Sin periodos",
                None,
            )

            return

        for periodo in periodos:

            self.periodo.addItem(
                ServicioNomina.nombre_periodo(
                    periodo,
                )
                + f" ({periodo.estado})",
                periodo.id,
            )

    def _nuevo_periodo(self) -> None:

        hoy = QDate.currentDate()

        try:

            ServicioNomina.crear_periodo(
                anio=hoy.year(),
                mes=hoy.month(),
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Nómina",
                str(error),
            )

            return

        self._cargar_periodos()

        QMessageBox.information(
            self,
            "Nómina",
            "Periodo creado correctamente.",
        )

    def _liquidar(self) -> None:

        periodo_id = self.periodo.currentData()

        if periodo_id is None:

            QMessageBox.warning(
                self,
                "Nómina",
                "Cree o seleccione un periodo.",
            )

            return

        try:

            total = ServicioNomina.liquidar_periodo(
                periodo_id,
                dias_trabajados=self.dias.value(),
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Nómina",
                str(error),
            )

            return

        self._cargar_periodos()

        self._consultar()

        QMessageBox.information(
            self,
            "Nómina",
            f"Se liquidaron {total} empleado(s).",
        )

    def _periodo_seleccionado(
        self,
    ) -> int | None:

        periodo_id = self.periodo.currentData()

        if periodo_id is None:

            QMessageBox.warning(
                self,
                "Nómina",
                "Cree o seleccione un periodo.",
            )

        return periodo_id

    def _exportar_pila(self) -> None:

        periodo_id = self._periodo_seleccionado()

        if periodo_id is None:

            return

        try:

            rutas = IntegracionNomina.exportar_pila(
                periodo_id,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "PILA",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "PILA",
            (
                "Archivos generados (Aportes en Línea):\n"
                f"Tipo 1: {rutas.get('tipo1') or 'N/A'}\n"
                f"Tipo 2: {rutas.get('tipo2')}"
            ),
        )

    def _contabilizar(self) -> None:

        periodo_id = self._periodo_seleccionado()

        if periodo_id is None:

            return

        try:

            IntegracionNomina.contabilizar(
                periodo_id,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Contabilidad",
                str(error),
            )

            return

        self._cargar_periodos()

        QMessageBox.information(
            self,
            "Contabilidad",
            "Liquidación contabilizada correctamente.",
        )

    def _emitir_dian(self) -> None:

        periodo_id = self._periodo_seleccionado()

        if periodo_id is None:

            return

        try:

            resultado = IntegracionNomina.emitir_electronica(
                periodo_id,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Nómina electrónica",
                str(error),
            )

            return

        self._cargar_periodos()

        QMessageBox.information(
            self,
            "Nómina electrónica",
            (
                f"Estado DIAN: {resultado.get('estado_dian', '')}\n"
                f"CUNE: {resultado['cune']}\n"
                f"XML: {resultado['ruta_xml']}\n"
                f"Mensaje: {resultado.get('mensaje', '')}"
            ),
        )

    def _consultar(self) -> None:

        periodo_id = self.periodo.currentData()

        if periodo_id is None:

            self.tabla.setRowCount(0)

            self.lbl_total.setText("")

            return

        filas = ServicioNomina.listar_resumen_periodo(
            periodo_id,
        )

        self.tabla.setRowCount(
            len(filas),
        )

        for i, fila in enumerate(filas):

            valores = [
                fila["codigo"],
                fila["empleado"],
                fila["documento"],
                formatear_moneda(
                    fila["devengado"],
                ),
                formatear_moneda(
                    fila["deducciones"],
                ),
                formatear_moneda(
                    fila["neto"],
                ),
                formatear_moneda(
                    fila["aportes"],
                ),
            ]

            for j, valor in enumerate(
                valores,
            ):

                self.tabla.setItem(
                    i,
                    j,
                    QTableWidgetItem(
                        valor,
                    ),
                )

        totales = ServicioNomina.totales_periodo(
            periodo_id,
        )

        self.lbl_total.setText(
            "Neto total: "
            f"{formatear_moneda(totales['neto'])}"
        )

        self.tabla.resizeColumnsToContents()
