from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from aplicacion.framework.ui.vista_documento import (
    VistaDocumento,
)
from aplicacion.modulos.compras.documentos_soporte.datasource import (
    DocumentoSoporteDataSource,
)


class VistaDocumentoSoporte(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = DocumentoSoporteDataSource()
        self._documento = None

        super().__init__(
            id_registro,
            parent=parent,
        )

    def _agregar_barras_accion(
        self,
    ) -> None:

        self.btn_emitir = self.boton_accion(
            "Emitir DS DIAN",
        )

        self.btn_cerrar = self.boton_accion(
            "Cerrar",
        )

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Documento soporte",
                (
                    self.btn_emitir,
                    self.btn_cerrar,
                ),
                separar_ultimo=True,
            ),
        )

    def _conectar_acciones(
        self,
    ) -> None:

        self.btn_emitir.clicked.connect(
            self._emitir_dian,
        )

        self.btn_cerrar.clicked.connect(
            self.cerrar.emit,
        )

    def _actualizar_botones(
        self,
    ) -> None:

        if self._documento is None:

            return

        self.btn_emitir.setEnabled(
            self._documento.estado
            not in (
                "emitido",
                "generado",
            )
        )

    def _emitir_dian(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Emitir documento soporte",
            "Se generará el XML del documento soporte "
            "y se enviará a la DIAN. "
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

            resultado = (
                self.datasource.emitir_electronica(
                    self.id_registro,
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Emisión DIAN",
                str(error),
            )

            return

        mensaje = (
            resultado.mensaje
            or resultado.error
            or "Proceso completado."
        )

        QMessageBox.information(
            self,
            "Emisión DIAN",
            mensaje,
        )

        self._cargar_datos()
        self.actualizado.emit()

    def _cargar_datos(
        self,
    ) -> None:

        documento = self.datasource.obtener_completa(
            self.id_registro,
        )

        if documento is None:

            QMessageBox.warning(
                self,
                "Documento soporte",
                "No se encontró el documento.",
            )

            self.cerrar.emit()

            return

        self._documento = documento

        titulo = f"Documento soporte {documento.numero}"

        if documento.razon_social_proveedor:

            titulo = (
                f"{titulo} — "
                f"{documento.razon_social_proveedor}"
            )

        self.lbl_titulo.setText(
            titulo,
        )

        estado = [
            documento.estado,
        ]

        if documento.estado_dian:

            estado.append(
                documento.estado_dian,
            )

        if documento.cuds:

            estado.append(
                "CUDS registrado",
            )

        self.mostrar_formato(
            " · ".join(estado),
        )

        filas = ""

        for detalle in documento.detalles:

            filas += (
                "<tr>"
                f"<td>{detalle.descripcion}</td>"
                f"<td align='right'>{detalle.cantidad:.2f}</td>"
                f"<td align='right'>${detalle.total_linea:,.2f}</td>"
                "</tr>"
            )

        html = (
            "<h2>Documento soporte en adquisiciones</h2>"
            f"<p><b>Proveedor:</b> "
            f"{documento.razon_social_proveedor or '-'}"
            f"<br><b>NIT:</b> "
            f"{documento.nit_proveedor or '-'}</p>"
            f"<p><b>Subtotal:</b> ${documento.subtotal:,.2f}<br>"
            f"<b>IVA:</b> ${documento.iva:,.2f}<br>"
            f"<b>Total:</b> ${documento.total:,.2f}</p>"
            "<table border='1' cellspacing='0' "
            "cellpadding='6' width='100%'>"
            "<tr><th>Descripción</th>"
            "<th>Cant.</th><th>Total</th></tr>"
            f"{filas}"
            "</table>"
        )

        self.establecer_html(
            html,
        )

        self._actualizar_botones()
