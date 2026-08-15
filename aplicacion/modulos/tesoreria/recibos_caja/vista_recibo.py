from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from aplicacion.framework.ui.vista_documento import (
    VistaDocumento,
)
from aplicacion.maestros.terceros.servicio import (
    TerceroServicio,
)
from aplicacion.modulos.tesoreria.recibos_caja.datasource import (
    ReciboCajaDataSource,
)
from aplicacion.modulos.tesoreria.recibos_caja.formatos_impresion import (
    generar_html_recibo,
)
from aplicacion.modulos.tesoreria.recibos_caja.impresion import (
    exportar_pdf_recibo_caja,
    imprimir_recibo_caja,
)


class VistaReciboCaja(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = ReciboCajaDataSource()
        self._recibo = None
        self._cliente = None
        self._nombre_cliente = ""

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
                "Recibo de caja",
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

        return "Recibo"

    def _actualizar_botones(
        self,
    ) -> None:

        if self._recibo is None:

            return

        self.btn_contabilizar.setEnabled(
            not self._recibo.contabilizado,
        )

        self.btn_editar_doc.setEnabled(
            self._recibo.estado == "borrador",
        )

    def _contabilizar(
        self,
    ) -> None:

        try:

            self.datasource.contabilizar(
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Contabilizar",
                str(
                    error,
                ),
            )

            return

        QMessageBox.information(
            self,
            "Contabilizar",
            "Recibo contabilizado.",
        )

        self._cargar_datos()
        self.actualizado.emit()

    def _editar(
        self,
    ) -> None:

        self.editar_solicitado.emit()

    def _cargar_datos(
        self,
    ) -> None:

        recibo = self.datasource.obtener_completo(
            self.id_registro,
        )

        if recibo is None:

            QMessageBox.warning(
                self,
                "Recibo",
                "No se encontró el recibo seleccionado.",
            )

            self.cerrar.emit()

            return

        cliente = TerceroServicio.obtener_por_id(
            recibo.cliente_id,
        )

        nombre_cliente = "Cliente"

        if cliente is not None:

            nombre_cliente = (
                cliente.razon_social
                or cliente.nombre_completo
                or nombre_cliente
            )

        self._recibo = recibo
        self._cliente = cliente
        self._nombre_cliente = nombre_cliente

        self.lbl_titulo.setText(
            f"Recibo {recibo.numero}",
        )

        self.mostrar_formato(
            recibo.estado,
        )

        documento = ""

        if cliente is not None:

            documento = str(
                cliente.numero_documento
                or "",
            )

        correo = ""

        telefono = ""

        if cliente is not None:

            correo = str(
                cliente.correo or "",
            )

            telefono = str(
                cliente.telefono
                or cliente.celular
                or "",
            )

        self.establecer_html(
            generar_html_recibo(
                recibo,
                nombre_cliente=nombre_cliente,
                documento_cliente=documento,
                correo_cliente=correo,
            ),
        )

        self._actualizar_botones()

    def _imprimir(
        self,
    ) -> None:

        if self._recibo is None:

            return

        documento = ""
        correo = ""
        telefono = ""

        if self._cliente is not None:

            documento = str(
                self._cliente.numero_documento
                or "",
            )

            correo = str(
                self._cliente.correo or "",
            )

            telefono = str(
                self._cliente.telefono
                or self._cliente.celular
                or "",
            )

        imprimir_recibo_caja(
            self._recibo,
            nombre_cliente=self._nombre_cliente,
            documento_cliente=documento,
            correo_cliente=correo,
            telefono_cliente=telefono,
            parent=self,
        )

    def _exportar_pdf(
        self,
    ) -> None:

        if self._recibo is None:

            return

        documento = ""
        correo = ""
        telefono = ""

        if self._cliente is not None:

            documento = str(
                self._cliente.numero_documento
                or "",
            )

            correo = str(
                self._cliente.correo or "",
            )

            telefono = str(
                self._cliente.telefono
                or self._cliente.celular
                or "",
            )

        exportar_pdf_recibo_caja(
            self._recibo,
            nombre_cliente=self._nombre_cliente,
            documento_cliente=documento,
            correo_cliente=correo,
            telefono_cliente=telefono,
            parent=self,
        )
