from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QMessageBox,
    QTableWidgetItem,
)

from aplicacion.framework.ui.inquiry_page import InquiryPage
from aplicacion.interfaz.kpis_inicio import (
    formatear_moneda,
)
from aplicacion.modulos.nomina.servicios import (
    ServicioNomina,
)


class PrestacionesNominaPage(InquiryPage):

    titulo = "Prestaciones sociales"

    _NOMBRE_EXPORT = "prestaciones_nomina"

    _COLUMNAS = [
        "Código",
        "Empleado",
        "Prima",
        "Cesantías",
        "Vacaciones",
        "Int. cesantías",
        "Total",
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

        self.lbl_total = QLabel()

        self._layout_filtros.addWidget(
            self.lbl_total,
        )

    def _agregar_botones_filtro(self) -> None:

        self._layout_filtros.addWidget(
            self._crear_boton(
                "Provisionar",
                self._provisionar,
            ),
        )

        self._layout_filtros.addWidget(
            self._crear_boton(
                "Prima semestral",
                self._prima_semestral,
            ),
        )

    def _prima_semestral(self) -> None:

        periodo_id = self.periodo.currentData()

        if periodo_id is None:

            QMessageBox.warning(
                self,
                "Prestaciones",
                "Seleccione un periodo.",
            )

            return

        try:

            filas = ServicioNomina.calcular_prima_semestral_periodo(
                periodo_id,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Prestaciones",
                str(error),
            )

            return

        total = sum(
            fila["prima_semestral"]
            for fila in filas
        )

        QMessageBox.information(
            self,
            "Prima semestral",
            (
                f"Empleados: {len(filas)}\n"
                f"Total estimado: {formatear_moneda(total)}"
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

    def _provisionar(self) -> None:

        periodo_id = self.periodo.currentData()

        if periodo_id is None:

            QMessageBox.warning(
                self,
                "Prestaciones",
                "Seleccione un periodo.",
            )

            return

        try:

            total = ServicioNomina.provisionar_prestaciones(
                periodo_id,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Prestaciones",
                str(error),
            )

            return

        self._consultar()

        QMessageBox.information(
            self,
            "Prestaciones",
            f"Se provisionaron {total} concepto(s).",
        )

    def _consultar(self) -> None:

        periodo_id = self.periodo.currentData()

        if periodo_id is None:

            self.tabla.setRowCount(0)

            self.lbl_total.setText("")

            return

        filas = ServicioNomina.listar_provisiones_periodo(
            periodo_id,
        )

        self.tabla.setRowCount(
            len(filas),
        )

        total_general = 0.0

        for i, fila in enumerate(filas):

            total_general += float(
                fila["total"],
            )

            valores = [
                fila["codigo"],
                fila["empleado"],
                formatear_moneda(
                    fila["prima"],
                ),
                formatear_moneda(
                    fila["cesantias"],
                ),
                formatear_moneda(
                    fila["vacaciones"],
                ),
                formatear_moneda(
                    fila.get(
                        "intereses_cesantias",
                        0,
                    ),
                ),
                formatear_moneda(
                    fila["total"],
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

        self.lbl_total.setText(
            "Total provisionado: "
            f"{formatear_moneda(total_general)}"
        )

        self.tabla.resizeColumnsToContents()
