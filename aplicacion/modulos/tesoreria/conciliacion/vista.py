from __future__ import annotations

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from aplicacion.modulos.tesoreria.conciliacion.servicios import (
    ServicioConciliacionBancaria,
)


class ConciliacionBancariaPage(QWidget):

    titulo = "Conciliación bancaria"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._construir()

    def _construir(self):
        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(
                "Importe extractos CSV y concilie "
                "automáticamente pagos con cartera "
                "y cuentas por pagar.",
            )
        )

        fila = QHBoxLayout()
        btn_importar = QPushButton(
            "Importar extracto CSV",
        )
        btn_importar.clicked.connect(
            self._importar,
        )
        btn_conciliar = QPushButton(
            "Conciliar automático",
        )
        btn_conciliar.clicked.connect(
            self._conciliar,
        )

        fila.addWidget(btn_importar)
        fila.addWidget(btn_conciliar)
        layout.addLayout(fila)

        self.lbl_resumen = QLabel("")
        layout.addWidget(self.lbl_resumen)

        self._actualizar_resumen()

    def _actualizar_resumen(self):
        resumen = (
            ServicioConciliacionBancaria.resumen()
        )

        self.lbl_resumen.setText(
            f"Movimientos: {resumen['total']} | "
            f"Conciliados: {resumen['conciliados']} | "
            f"Pendientes: {resumen['pendientes']}"
        )

    def _importar(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Importar extracto",
            "",
            "CSV (*.csv);;Todos (*.*)",
        )

        if not ruta:
            return

        cantidad = (
            ServicioConciliacionBancaria.importar_csv(
                ruta,
            )
        )

        self.lbl_resumen.setText(
            f"Importados: {cantidad} movimiento(s).",
        )
        self._actualizar_resumen()

    def _conciliar(self):
        resultado = (
            ServicioConciliacionBancaria
            .conciliar_automatico()
        )

        self.lbl_resumen.setText(
            f"Conciliados: {resultado['conciliados']} | "
            f"Pendientes: {resultado['pendientes']}"
        )
