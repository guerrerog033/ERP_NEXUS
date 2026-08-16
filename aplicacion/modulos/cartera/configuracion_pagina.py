from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QMessageBox,
    QSpinBox,
)

from aplicacion.framework.base.page import Page
from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.recursos.ui.botones import Botones


class ConfiguracionCarteraPage(Page):

    titulo = "Configuración de cartera"

    def _crear_ui(self):

        super()._crear_ui()

        grupo = QGroupBox(
            "Bloqueo por cartera vencida",
        )

        formulario = QFormLayout(grupo)

        self.bloquear_por_mora = QCheckBox(
            "Bloquear la creación de nuevas facturas de venta a "
            "clientes con cartera vencida",
        )

        self.dias_gracia = QSpinBox()
        self.dias_gracia.setRange(0, 365)
        self.dias_gracia.setSuffix(" días")

        formulario.addRow(
            "",
            self.bloquear_por_mora,
        )
        formulario.addRow(
            "Días de gracia tras el vencimiento",
            self.dias_gracia,
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

        self.bloquear_por_mora.setChecked(
            bool(
                obtener(
                    "cartera",
                    "bloquear_facturacion_por_mora",
                ),
            ),
        )

        self.dias_gracia.setValue(
            int(
                obtener(
                    "cartera",
                    "dias_gracia_mora",
                )
                or 0,
            ),
        )

    def _guardar(self):

        try:

            actualizar = Configuracion.actualizar

            actualizar(
                (
                    "cartera",
                    "bloquear_facturacion_por_mora",
                ),
                self.bloquear_por_mora.isChecked(),
            )

            actualizar(
                (
                    "cartera",
                    "dias_gracia_mora",
                ),
                self.dias_gracia.value(),
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
            "Configuración de cartera",
            "Configuración guardada correctamente.",
        )
