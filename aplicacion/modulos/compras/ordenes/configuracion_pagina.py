from __future__ import annotations

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QMessageBox,
)

from aplicacion.framework.base.page import Page
from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.recursos.ui.botones import Botones


class ConfiguracionAprobacionComprasPage(Page):

    titulo = "Aprobación de órdenes de compra"

    def _crear_ui(self):

        super()._crear_ui()

        grupo = QGroupBox(
            "Montos que requieren aprobación",
        )

        formulario = QFormLayout(grupo)

        self.monto_nivel1 = QDoubleSpinBox()
        self.monto_nivel1.setRange(0, 999999999)
        self.monto_nivel1.setDecimals(0)
        self.monto_nivel1.setGroupSeparatorShown(True)

        self.monto_nivel2 = QDoubleSpinBox()
        self.monto_nivel2.setRange(0, 999999999)
        self.monto_nivel2.setDecimals(0)
        self.monto_nivel2.setGroupSeparatorShown(True)

        formulario.addRow(
            "Requiere aprobación desde (0 = deshabilitado)",
            self.monto_nivel1,
        )
        formulario.addRow(
            "Requiere segunda aprobación desde "
            "(0 = deshabilitado)",
            self.monto_nivel2,
        )

        self.agregar_widget(grupo)

        self.agregar_stretch()

        botones = QHBoxLayout()

        self.btn_guardar = Botones.guardar()
        self.btn_guardar.clicked.connect(
            self._guardar,
        )

        botones.addWidget(self.btn_guardar)
        botones.addStretch()

        self.agregar_layout(botones)

        self._cargar_datos()

    def _cargar_datos(self):

        obtener = Configuracion.obtener

        self.monto_nivel1.setValue(
            float(
                obtener(
                    "compras",
                    "aprobacion_nivel1_monto",
                )
                or 0,
            ),
        )

        self.monto_nivel2.setValue(
            float(
                obtener(
                    "compras",
                    "aprobacion_nivel2_monto",
                )
                or 0,
            ),
        )

    def _guardar(self):

        if (
            self.monto_nivel2.value() > 0
            and self.monto_nivel1.value() > 0
            and self.monto_nivel2.value()
            < self.monto_nivel1.value()
        ):

            QMessageBox.warning(
                self,
                "Aprobación de compras",
                "El monto de segunda aprobación no puede ser "
                "menor que el de primera aprobación.",
            )

            return

        try:

            actualizar = Configuracion.actualizar

            actualizar(
                ("compras", "aprobacion_nivel1_monto"),
                self.monto_nivel1.value(),
            )

            actualizar(
                ("compras", "aprobacion_nivel2_monto"),
                self.monto_nivel2.value(),
            )

        except OSError as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar la configuración: {error}",
            )

            return

        QMessageBox.information(
            self,
            "Aprobación de compras",
            "Configuración guardada correctamente.",
        )
