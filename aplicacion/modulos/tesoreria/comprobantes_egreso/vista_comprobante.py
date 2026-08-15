from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from aplicacion.framework.ui.vista_documento import (
    VistaDocumento,
)
from aplicacion.maestros.terceros.servicio import (
    TerceroServicio,
)
from aplicacion.modulos.tesoreria.comprobantes_egreso.datasource import (
    ComprobanteEgresoDataSource,
)
from aplicacion.modulos.tesoreria.comprobantes_egreso.formatos_impresion import (
    generar_html_comprobante,
)
from aplicacion.modulos.tesoreria.comprobantes_egreso.impresion import (
    exportar_pdf_comprobante_egreso,
    imprimir_comprobante_egreso,
)


class VistaComprobanteEgreso(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = ComprobanteEgresoDataSource()
        self._comprobante = None
        self._proveedor = None
        self._nombre_proveedor = ""

        super().__init__(
            id_registro,
            parent=parent,
        )

    def _agregar_barras_accion(
        self,
    ) -> None:

        self.btn_contabilizar = self.boton_accion(
            "Contabilizar",
        )

        self.btn_editar_doc = self.boton_accion(
            "Editar",
        )

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Documento",
                (
                    self.btn_contabilizar,
                    self.btn_editar_doc,
                ),
            ),
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
                "Comprobante de egreso",
                (
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

        self.btn_contabilizar.clicked.connect(
            self._contabilizar,
        )

        self.btn_editar_doc.clicked.connect(
            self._editar,
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

    def etiqueta_barra_principal(
        self,
    ) -> str:

        return "Egreso"

    def _actualizar_botones(
        self,
    ) -> None:

        if self._comprobante is None:

            return

        self.btn_contabilizar.setEnabled(
            not self._comprobante.contabilizado,
        )

        self.btn_editar_doc.setEnabled(
            not self._comprobante.contabilizado,
        )

    def _editar(
        self,
    ) -> None:

        self.editar_solicitado.emit()

    def _contabilizar(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Contabilizar",
            "Se registrará el asiento contable y "
            "se actualizarán los saldos de las facturas. "
            "¿Desea continuar?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if (
            confirmar
            != QMessageBox.StandardButton.Yes
        ):

            return

        try:

            self.datasource.contabilizar(
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Contabilizar",
                str(error),
            )

            return

        except Exception as error:

            QMessageBox.critical(
                self,
                "Contabilizar",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Contabilizar",
            "Comprobante contabilizado correctamente.",
        )

        self._cargar_datos()
        self.actualizado.emit()

    def _cargar_datos(
        self,
    ) -> None:

        comprobante = self.datasource.obtener_completo(
            self.id_registro,
        )

        if comprobante is None:

            QMessageBox.warning(
                self,
                "Comprobante",
                "No se encontró el comprobante seleccionado.",
            )

            self.cerrar.emit()

            return

        proveedor = TerceroServicio.obtener_por_id(
            comprobante.proveedor_id,
        )

        nombre_proveedor = "Proveedor"

        documento = ""

        if proveedor is not None:

            nombre_proveedor = (
                proveedor.razon_social
                or proveedor.nombre_completo
                or nombre_proveedor
            )

            documento = str(
                proveedor.numero_documento or "",
            )

        self._comprobante = comprobante
        self._proveedor = proveedor
        self._nombre_proveedor = nombre_proveedor

        self.lbl_titulo.setText(
            f"Comprobante {comprobante.numero}",
        )

        self.mostrar_formato(
            comprobante.estado,
        )

        self.establecer_html(
            generar_html_comprobante(
                comprobante,
                nombre_proveedor=nombre_proveedor,
                documento_proveedor=documento,
            ),
        )

        self._actualizar_botones()

    def _imprimir(
        self,
    ) -> None:

        if self._comprobante is None:

            return

        documento = ""

        if self._proveedor is not None:

            documento = str(
                self._proveedor.numero_documento
                or "",
            )

        imprimir_comprobante_egreso(
            self._comprobante,
            nombre_proveedor=self._nombre_proveedor,
            documento_proveedor=documento,
            parent=self,
        )

    def _exportar_pdf(
        self,
    ) -> None:

        if self._comprobante is None:

            return

        documento = ""

        if self._proveedor is not None:

            documento = str(
                self._proveedor.numero_documento
                or "",
            )

        exportar_pdf_comprobante_egreso(
            self._comprobante,
            nombre_proveedor=self._nombre_proveedor,
            documento_proveedor=documento,
            parent=self,
        )
