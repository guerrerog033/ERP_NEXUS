from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from aplicacion.modulos.contabilidad.reglas.servicio_reglas import (
    ServicioReglasContabilizacion,
)


class ReglasContabilizacionPage(QWidget):

    titulo = "Reglas contables"

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(
                "Reglas configurables para contabilización "
                "automática de compras (inventario, gastos, IVA).",
            )
        )

        ServicioReglasContabilizacion.inicializar_defecto()

        for regla in ServicioReglasContabilizacion.listar():
            layout.addWidget(
                QLabel(
                    f"<b>{regla.nombre}</b> — "
                    f"{regla.criterio}={regla.valor_criterio} → "
                    f"Débito {regla.cuenta_debito}, "
                    f"Crédito {regla.cuenta_credito or '220501'}"
                )
            )

        layout.addStretch()
