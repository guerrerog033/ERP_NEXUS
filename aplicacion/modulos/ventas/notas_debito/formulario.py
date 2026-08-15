from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
)

from aplicacion.modulos.ventas.facturas.formulario import (
    FormularioFacturaVenta,
)
from aplicacion.modulos.ventas.notas_debito.datasource import (
    NotaDebitoVentaDataSource,
)
from aplicacion.modulos.ventas.notas_debito.nota_definition import (
    NotaDebitoVentaDefinition,
)
from aplicacion.modulos.ventas.notas_debito.servicios import (
    MOTIVOS_NOTA_DEBITO,
)


class FormularioNotaDebitoVenta(
    FormularioFacturaVenta,
):

    titulo = "Nota débito de venta"

    definition = NotaDebitoVentaDefinition

    def __init__(
        self,
        id_registro=None,
        parent=None,
    ):

        self.factura_id = None

        super().__init__(
            id_registro=id_registro,
            parent=parent,
        )

        self.datasource = NotaDebitoVentaDataSource()

    def _adaptar_interfaz_factura(
        self,
    ):

        super()._adaptar_interfaz_factura()

        self.titulo = "Nota débito de venta"

        self.lbl_factura_ref = QLabel(
            "Factura:",
        )

        self.lbl_factura_ref.setStyleSheet(
            "font-weight:600;color:#1B4F8A;",
        )

        self.txt_factura_ref = QLabel(
            "-",
        )

        self.cmb_motivo = QComboBox()

        for motivo in MOTIVOS_NOTA_DEBITO:

            self.cmb_motivo.addItem(
                motivo,
            )

        cabecera = self.card.contenido.itemAt(
            0,
        ).widget()

        grid = cabecera.layout()

        if isinstance(
            grid,
            QGridLayout,
        ):

            fila = grid.rowCount()

            grid.addWidget(
                self.lbl_factura_ref,
                fila,
                0,
            )

            grid.addWidget(
                self.txt_factura_ref,
                fila,
                1,
            )

            grid.addWidget(
                QLabel("Motivo:"),
                fila,
                2,
            )

            grid.addWidget(
                self.cmb_motivo,
                fila,
                3,
            )

        if hasattr(
            self,
            "cmb_forma_pago",
        ):

            self.cmb_forma_pago.parentWidget().hide()

    def _cargar_registro(
        self,
    ):

        nota = self.datasource.obtener_completa(
            self.id_registro,
        )

        if nota is None:

            return

        self.factura_id = nota.factura_id

        self.txt_factura_ref.setText(
            str(
                nota.factura_id,
            ),
        )

        if nota.motivo:

            indice = self.cmb_motivo.findText(
                nota.motivo,
            )

            if indice >= 0:

                self.cmb_motivo.setCurrentIndex(
                    indice,
                )

        super()._cargar_registro()

    def _obtener_cabecera(
        self,
    ) -> dict:

        cabecera = super()._obtener_cabecera()

        cabecera["factura_id"] = self.factura_id
        cabecera["motivo"] = (
            self.cmb_motivo.currentText().strip()
        )

        return cabecera

    def guardar(
        self,
    ):

        from PySide6.QtWidgets import (
            QMessageBox,
        )

        try:

            nota = self.datasource.guardar_completa(
                self._obtener_cabecera(),
                self._obtener_lineas(),
                self.id_registro,
            )

            self.id_registro = nota.id

            self.es_edicion = True

            self.txt_numero.setText(
                nota.numero,
            )

            QMessageBox.information(
                self,
                "Información",
                "Nota débito guardada correctamente.",
            )

            self.guardado.emit()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                str(error),
            )
