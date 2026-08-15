from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
)

from aplicacion.framework.crud.crud_documento import CrudDocumento
from aplicacion.framework.crud.crud_master import CrudMaster
from aplicacion.modulos.ventas.notas_debito.datasource import (
    NotaDebitoVentaDataSource,
)
from aplicacion.modulos.ventas.notas_debito.formulario import (
    FormularioNotaDebitoVenta,
)
from aplicacion.modulos.ventas.notas_debito.servicios import (
    ServicioNotaDebitoVenta,
)
from aplicacion.modulos.ventas.notas_debito.vista import (
    VistaNotaDebitoVenta,
)


class MaestroNotasDebitoVenta(
    CrudDocumento,
    CrudMaster,
):

    titulo = "Notas débito de venta"

    titulo_singular = "Nota débito de venta"

    datasource = NotaDebitoVentaDataSource

    formulario = FormularioNotaDebitoVenta

    vista_documento = VistaNotaDebitoVenta

    def nuevo(self):

        factura_id = self._seleccionar_factura()

        if factura_id is None:

            return

        try:

            nota = ServicioNotaDebitoVenta.crear_desde_factura(
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
            ServicioNotaDebitoVenta.listar_facturas_emitidas()
        )

        if not facturas:

            self.mostrar_error(
                "No hay facturas emitidas disponibles.",
            )

            return None

        dialogo = QDialog(
            self,
        )

        dialogo.setWindowTitle(
            "Seleccionar factura",
        )

        layout = QVBoxLayout(
            dialogo,
        )

        combo = QComboBox()

        for factura in facturas:

            etiqueta = (
                f"{factura.numero} · "
                f"{factura.fecha} · "
                f"${float(factura.total or 0):,.0f}"
            )

            combo.addItem(
                etiqueta,
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

            return "Nota débito de venta"

        return f"Nota débito {nota.numero}"

    def _titulo_dialogo_formulario(
        self,
        id_registro=None,
    ) -> str:

        if id_registro is not None:

            return "Editar nota débito"

        return "Nueva nota débito"
