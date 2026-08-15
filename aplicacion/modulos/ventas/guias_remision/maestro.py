from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from aplicacion.framework.crud.crud_documento import (
    CrudDocumento,
)
from aplicacion.framework.crud.crud_master import (
    CrudMaster,
)
from aplicacion.modulos.ventas.guias_remision.datasource import (
    GuiaRemisionElectronicaDataSource,
)
from aplicacion.modulos.ventas.guias_remision.servicios import (
    ServicioGuiaRemisionElectronica,
)
from aplicacion.modulos.ventas.guias_remision.vista import (
    VistaGuiaRemisionElectronica,
)
from aplicacion.modulos.ventas.remisiones.repositorio import (
    RepositorioRemision,
)


class MaestroGuiasRemisionElectronica(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Guías remisión electrónica"

    titulo_singular = "Guía remisión electrónica"

    datasource = GuiaRemisionElectronicaDataSource

    vista_documento = VistaGuiaRemisionElectronica

    def nuevo(self):

        remision_id = self._seleccionar_remision()

        if remision_id is None:

            return

        transporte = self._solicitar_transporte()

        if transporte is None:

            return

        try:

            guia = (
                ServicioGuiaRemisionElectronica
                .crear_desde_remision(
                    remision_id,
                    **transporte,
                )
            )

        except ValueError as error:

            self.mostrar_error(
                str(error),
            )

            return

        self.cargar_datos()

        self.mostrar_vista_documento(
            guia.id,
        )

    def _seleccionar_remision(
        self,
    ) -> int | None:

        remisiones = RepositorioRemision.buscar(
            "",
        )

        if not remisiones:

            self.mostrar_error(
                "No hay remisiones internas disponibles.",
            )

            return None

        dialogo = QDialog(
            self,
        )

        dialogo.setWindowTitle(
            "Seleccionar remisión interna",
        )

        layout = QVBoxLayout(
            dialogo,
        )

        combo = QComboBox()

        for remision in remisiones:

            combo.addItem(
                (
                    f"{remision.numero} · "
                    f"{remision.fecha} · "
                    f"{remision.estado}"
                ),
                remision.id,
            )

        layout.addWidget(
            combo,
        )

        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
        )

        botones.accepted.connect(
            dialogo.accept,
        )

        botones.rejected.connect(
            dialogo.reject,
        )

        layout.addWidget(
            botones,
        )

        if dialogo.exec() != QDialog.DialogCode.Accepted:

            return None

        return combo.currentData()

    def _solicitar_transporte(
        self,
    ) -> dict | None:

        dialogo = QDialog(
            self,
        )

        dialogo.setWindowTitle(
            "Datos de transporte",
        )

        layout = QVBoxLayout(
            dialogo,
        )

        form = QFormLayout()

        conductor = QLineEdit()
        vehiculo = QLineEdit()
        placa = QLineEdit()
        transportadora = QLineEdit()

        form.addRow(
            "Conductor:",
            conductor,
        )

        form.addRow(
            "Vehículo:",
            vehiculo,
        )

        form.addRow(
            "Placa:",
            placa,
        )

        form.addRow(
            "Transportadora:",
            transportadora,
        )

        layout.addLayout(
            form,
        )

        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
        )

        botones.accepted.connect(
            dialogo.accept,
        )

        botones.rejected.connect(
            dialogo.reject,
        )

        layout.addWidget(
            botones,
        )

        if dialogo.exec() != QDialog.DialogCode.Accepted:

            return None

        return {
            "conductor": conductor.text().strip(),
            "vehiculo": vehiculo.text().strip(),
            "placa": placa.text().strip(),
            "transportadora": (
                transportadora.text().strip()
            ),
        }

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        guia = self.datasource.obtener_completa(
            id_registro,
        )

        if guia is None:

            return "Guía remisión electrónica"

        return f"Guía {guia.numero}"
