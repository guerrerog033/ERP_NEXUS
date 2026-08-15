from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
)

from aplicacion.framework.crud.crud_documento import (
    CrudDocumento,
)
from aplicacion.framework.crud.crud_master import (
    CrudMaster,
)
from aplicacion.modulos.compras.notas_credito.datasource import (
    NotaCreditoCompraDataSource,
)
from aplicacion.modulos.compras.notas_credito.servicios import (
    ServicioNotaCreditoCompra,
)
from aplicacion.modulos.compras.notas_credito.vista import (
    VistaNotaCreditoCompra,
)


class MaestroNotasCreditoCompra(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Notas crédito de compra"

    titulo_singular = "Nota crédito de compra"

    datasource = NotaCreditoCompraDataSource

    vista_documento = VistaNotaCreditoCompra

    def nuevo(self):

        factura_id = self._seleccionar_factura()

        if factura_id is None:

            return

        try:

            nota = ServicioNotaCreditoCompra.crear_desde_factura(
                factura_id,
            )

        except ValueError as error:

            self.mostrar_error(
                str(error),
            )

            return

        self.cargar_datos()

        self.mostrar_vista_documento(
            nota.id,
        )

    def _seleccionar_factura(
        self,
    ) -> int | None:

        facturas = (
            ServicioNotaCreditoCompra
            .listar_facturas_contabilizadas()
        )

        if not facturas:

            self.mostrar_error(
                "No hay facturas de compra "
                "contabilizadas disponibles.",
            )

            return None

        dialogo = QDialog(
            self,
        )

        dialogo.setWindowTitle(
            "Seleccionar factura de compra",
        )

        layout = QVBoxLayout(
            dialogo,
        )

        combo = QComboBox()

        for factura in facturas:

            combo.addItem(
                (
                    f"{factura.numero} · "
                    f"{factura.fecha} · "
                    f"${float(factura.total or 0):,.0f}"
                ),
                factura.id,
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

    def _titulo_dialogo_vista(
        self,
        id_registro: int,
    ) -> str:

        nota = self.datasource.obtener_completa(
            id_registro,
        )

        if nota is None:

            return "Nota crédito de compra"

        return f"NC compra {nota.numero}"
