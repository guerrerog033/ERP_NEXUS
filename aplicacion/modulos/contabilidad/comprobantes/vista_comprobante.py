from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from aplicacion.framework.ui.vista_documento import (
    VistaDocumento,
)
from aplicacion.modulos.contabilidad.comprobantes.datasource import (
    ComprobanteDataSource,
)
from aplicacion.modulos.contabilidad.comprobantes.formatos_impresion import (
    generar_html_comprobante_contable,
)
from aplicacion.modulos.contabilidad.comprobantes.impresion import (
    exportar_pdf_comprobante_contable,
    imprimir_comprobante_contable,
)


class VistaComprobante(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = ComprobanteDataSource()

        self._asiento = None

        super().__init__(
            id_registro,
            parent=parent,
        )

    def etiqueta_barra_principal(
        self,
    ) -> str:

        return "Comprobante"

    def _agregar_barras_accion(
        self,
    ) -> None:

        self.btn_editar_doc = self.boton_accion(
            "Editar",
        )

        self.btn_imprimir = self.boton_accion(
            "Imprimir",
        )

        self.btn_pdf = self.boton_accion(
            "PDF",
        )

        self.btn_cerrar = self.boton_accion(
            "Cerrar",
        )

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Comprobante",
                (
                    self.btn_editar_doc,
                    self.btn_imprimir,
                    self.btn_pdf,
                    self.btn_cerrar,
                ),
                separar_ultimo=True,
            ),
        )

    def _conectar_acciones(
        self,
    ) -> None:

        self.btn_editar_doc.clicked.connect(
            self.editar_solicitado.emit,
        )

        self.btn_imprimir.clicked.connect(
            self._imprimir,
        )

        self.btn_pdf.clicked.connect(
            self._exportar_pdf,
        )

        self.btn_cerrar.clicked.connect(
            self.cerrar.emit,
        )

    def _cargar_datos(
        self,
    ) -> None:

        asiento = self.datasource.obtener_completo(
            self.id_registro,
        )

        if asiento is None:

            self.cerrar.emit()

            return

        self._asiento = asiento

        self.lbl_titulo.setText(
            f"Comprobante {asiento.numero}",
        )

        self.mostrar_formato(
            f"{asiento.origen} · "
            f"D {asiento.total_debito:,.2f} · "
            f"C {asiento.total_credito:,.2f}",
        )

        self.establecer_html(
            generar_html_comprobante_contable(
                asiento,
            ),
        )

        editable = (
            asiento.origen == "manual"
        )

        self.btn_editar_doc.setEnabled(
            editable,
        )

    def _imprimir(
        self,
    ) -> None:

        if self._asiento is None:

            return

        imprimir_comprobante_contable(
            self._asiento,
            parent=self,
        )

    def _exportar_pdf(
        self,
    ) -> None:

        if self._asiento is None:

            return

        exportar_pdf_comprobante_contable(
            self._asiento,
            parent=self,
        )

    def recargar(
        self,
    ) -> None:

        self._cargar_datos()
