from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QMessageBox,
)

from aplicacion.framework.ui.vista_documento import (
    VistaDocumento,
)
from aplicacion.maestros.terceros.servicio import (
    TerceroServicio,
)
from aplicacion.modulos.ventas.facturas.datasource import (
    FacturaVentaDataSource,
)
from aplicacion.modulos.ventas.facturas.formatos_impresion import (
    etiqueta_formato,
    formatos_combo,
    generar_html_factura_venta,
    normalizar_formato_codigo,
)
from aplicacion.modulos.ventas.facturas.impresion import (
    exportar_pdf_factura_venta,
    imprimir_factura_venta,
)
from aplicacion.recursos.ui.botones import Botones


class VistaFacturaVenta(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = FacturaVentaDataSource()

        self._factura = None
        self._detalles: list = []
        self._nombre_cliente = ""
        self._cargando_formato = False

        super().__init__(
            id_registro,
            parent=parent,
        )

    def _agregar_barras_accion(
        self,
    ) -> None:

        self.btn_confirmar = self.boton_accion(
            "Confirmar",
        )

        self.btn_emitir = self.boton_accion(
            "Emitir FE DIAN",
        )

        self.btn_contabilizar = self.boton_accion(
            "Contabilizar",
        )

        self.btn_nota_credito = self.boton_accion(
            "Nota crédito",
        )

        self.btn_nota_debito = self.boton_accion(
            "Nota débito",
        )

        self.btn_cartera = self.boton_accion(
            "Cartera cliente",
        )

        self.btn_estado_cuenta = self.boton_accion(
            "Estado de cuenta",
        )

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Documento",
                (
                    self.btn_confirmar,
                    self.btn_emitir,
                    self.btn_contabilizar,
                    self.btn_cartera,
                    self.btn_estado_cuenta,
                    self.btn_nota_credito,
                    self.btn_nota_debito,
                ),
            ),
        )

        self.btn_editar = Botones.editar()

        self.lbl_formato_impresion = QLabel(
            "Formato",
        )

        self.lbl_formato_impresion.setStyleSheet(
            "color: #475569; font-weight: 600;",
        )

        self.cmb_formato = QComboBox()

        self.cmb_formato.setMinimumWidth(
            180,
        )

        for (
            etiqueta,
            codigo,
        ) in formatos_combo():

            self.cmb_formato.addItem(
                etiqueta,
                codigo,
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
                self.etiqueta_barra_principal(),
                (
                    self.btn_editar,
                    self.lbl_formato_impresion,
                    self.cmb_formato,
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

        self.btn_confirmar.clicked.connect(
            self._confirmar_venta,
        )

        self.btn_emitir.clicked.connect(
            self._emitir_dian,
        )

        self.btn_contabilizar.clicked.connect(
            self._contabilizar,
        )

        self.btn_nota_credito.clicked.connect(
            self._crear_nota_credito,
        )

        self.btn_nota_debito.clicked.connect(
            self._crear_nota_debito,
        )

        self.btn_cartera.clicked.connect(
            self._ver_cartera_cliente,
        )

        self.btn_estado_cuenta.clicked.connect(
            self._ver_estado_cuenta_cliente,
        )

        self.btn_editar.clicked.connect(
            self.editar_solicitado.emit,
        )

        self.cmb_formato.currentIndexChanged.connect(
            self._cambiar_formato_impresion,
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

        return "Factura venta"

    def _etiqueta_estado(
        self,
    ) -> str:

        if self._factura is None:

            return ""

        partes = [
            self._factura.estado,
        ]

        if self._factura.estado_dian:

            partes.append(
                self._factura.estado_dian,
            )

        if self._factura.cufe:

            partes.append(
                "CUFE registrado",
            )

        if self._factura.contabilizado:

            partes.append(
                "contabilizada",
            )

        return " · ".join(partes)

    def _actualizar_botones(
        self,
    ) -> None:

        if self._factura is None:

            return

        self.btn_confirmar.setEnabled(
            self._factura.estado
            == "borrador",
        )

        self.btn_emitir.setEnabled(
            self._factura.estado
            not in (
                "emitida",
                "contabilizada",
            )
        )

        self.btn_contabilizar.setEnabled(
            not self._factura.contabilizado
            and self._factura.estado
            not in (
                "borrador",
            )
        )

        self.btn_nota_credito.setEnabled(
            self._factura.estado
            in (
                "emitida",
                "generada",
                "contabilizada",
            )
        )

        self.btn_nota_debito.setEnabled(
            self._factura.estado
            in (
                "emitida",
                "generada",
                "contabilizada",
            )
        )

        editable = (
            str(
                self._factura.estado or "",
            ).lower()
            == "borrador"
        )

        self.btn_editar.setVisible(
            editable,
        )

        self.btn_editar.setEnabled(
            editable,
        )

    def _crear_nota_credito(
        self,
    ) -> None:

        from PySide6.QtWidgets import (
            QDialog,
            QVBoxLayout,
        )

        from aplicacion.modulos.ventas.notas_credito.servicios import (
            ServicioNotaCreditoVenta,
        )
        from aplicacion.modulos.ventas.notas_credito.vista import (
            VistaNotaCreditoVenta,
        )

        confirmar = QMessageBox.question(
            self,
            "Nota crédito",
            "Se creará una nota crédito con las "
            "mismas líneas de esta factura. "
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

            nota = (
                ServicioNotaCreditoVenta.crear_desde_factura(
                    self.id_registro,
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Nota crédito",
                str(error),
            )

            return

        ventana = QDialog(
            self,
        )

        ventana.setWindowTitle(
            f"Nota crédito {nota.numero}",
        )

        ventana.setModal(
            True,
        )

        ventana.resize(
            1120,
            720,
        )

        layout = QVBoxLayout(
            ventana,
        )

        vista = VistaNotaCreditoVenta(
            id_registro=nota.id,
            parent=ventana,
        )

        layout.addWidget(
            vista,
        )

        vista.cerrar.connect(
            ventana.accept,
        )

        ventana.exec()

        vista.deleteLater()

    def _crear_nota_debito(
        self,
    ) -> None:

        from PySide6.QtWidgets import (
            QDialog,
            QVBoxLayout,
        )

        from aplicacion.modulos.ventas.notas_debito.servicios import (
            ServicioNotaDebitoVenta,
        )
        from aplicacion.modulos.ventas.notas_debito.vista import (
            VistaNotaDebitoVenta,
        )

        confirmar = QMessageBox.question(
            self,
            "Nota débito",
            "Se creará una nota débito referenciando "
            "esta factura para registrar cargos "
            "adicionales. ¿Desea continuar?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if (
            confirmar
            != QMessageBox.StandardButton.Yes
        ):

            return

        try:

            nota = (
                ServicioNotaDebitoVenta.crear_desde_factura(
                    self.id_registro,
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Nota débito",
                str(error),
            )

            return

        ventana = QDialog(
            self,
        )

        ventana.setWindowTitle(
            f"Nota débito {nota.numero}",
        )

        ventana.setModal(
            True,
        )

        ventana.resize(
            1120,
            720,
        )

        layout = QVBoxLayout(
            ventana,
        )

        vista = VistaNotaDebitoVenta(
            id_registro=nota.id,
            parent=ventana,
        )

        layout.addWidget(
            vista,
        )

        vista.cerrar.connect(
            ventana.accept,
        )

        ventana.exec()

        vista.deleteLater()

    def _ver_cartera_cliente(
        self,
    ) -> None:

        from aplicacion.modulos.cartera.ui_comercial import (
            cartera_desde_documento,
        )

        cartera_desde_documento(
            self,
            self._factura,
            nombre_cliente=self._nombre_cliente,
        )

    def _ver_estado_cuenta_cliente(
        self,
    ) -> None:

        from aplicacion.modulos.cartera.ui_comercial import (
            estado_cuenta_desde_documento,
        )

        estado_cuenta_desde_documento(
            self,
            self._factura,
            nombre_cliente=self._nombre_cliente,
        )

    def _confirmar_venta(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Confirmar factura",
            "Se aplicará el efecto comercial "
            "(inventario y contabilidad según "
            "configuración) sin enviar a la DIAN. "
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

            factura = self.datasource.confirmar_venta(
                self.id_registro,
                emitir_dian=False,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Confirmar factura",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Confirmar factura",
            f"Factura {factura.numero} confirmada.",
        )

        self._cargar_datos()
        self.actualizado.emit()

    def _contabilizar(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Contabilizar",
            "Se registrará el asiento contable de "
            "esta factura de venta. "
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

            asiento = self.datasource.contabilizar(
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Contabilizar",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Contabilizar",
            f"Asiento {asiento.numero} registrado.",
        )

        self._cargar_datos()
        self.actualizado.emit()

    def _formato_actual(
        self,
    ) -> str:

        if self._factura is None:

            return normalizar_formato_codigo(
                self.cmb_formato.currentData(),
            )

        return normalizar_formato_codigo(
            self._factura.formato_impresion,
        )

    def _actualizar_vista_previa(
        self,
    ) -> None:

        if self._factura is None:

            return

        formato = self._formato_actual()

        self.mostrar_formato(
            f"{self._etiqueta_estado()} · "
            f"Formato: {etiqueta_formato(formato)}",
        )

        self.establecer_html(
            generar_html_factura_venta(
                self._factura,
                self._detalles,
                self._nombre_cliente,
                formato=formato,
            ),
        )

    def _sincronizar_combo_formato(
        self,
    ) -> None:

        if self._factura is None:

            return

        formato = normalizar_formato_codigo(
            self._factura.formato_impresion,
        )

        indice = self.cmb_formato.findData(
            formato,
        )

        self._cargando_formato = True

        if indice >= 0:

            self.cmb_formato.setCurrentIndex(
                indice,
            )

        self._cargando_formato = False

    def _cambiar_formato_impresion(
        self,
    ) -> None:

        if (
            self._cargando_formato
            or self._factura is None
        ):

            return

        formato = normalizar_formato_codigo(
            self.cmb_formato.currentData(),
        )

        if (
            normalizar_formato_codigo(
                self._factura.formato_impresion,
            )
            == formato
        ):

            self._actualizar_vista_previa()

            return

        try:

            factura = (
                self.datasource.actualizar_formato_impresion(
                    self.id_registro,
                    formato,
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Formato de impresión",
                str(error),
            )

            self._sincronizar_combo_formato()

            return

        self._factura = factura

        self._actualizar_vista_previa()

    def _emitir_dian(
        self,
    ) -> None:

        try:

            resultado = (
                self.datasource.emitir_electronica(
                    self.id_registro,
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Emitir FE",
                str(error),
            )

            return

        mensaje = (
            resultado.mensaje
            or resultado.error
            or "Proceso completado."
        )

        if resultado.exito:

            QMessageBox.information(
                self,
                "Emitir FE",
                mensaje,
            )

        else:

            QMessageBox.warning(
                self,
                "Emitir FE",
                mensaje,
            )

        self._cargar_datos()
        self.actualizado.emit()

    def _cargar_datos(
        self,
    ) -> None:

        factura = self.datasource.obtener_completa(
            self.id_registro,
        )

        if factura is None:

            QMessageBox.warning(
                self,
                "Factura de venta",
                "No se encontró la factura seleccionada.",
            )

            self.cerrar.emit()

            return

        cliente = TerceroServicio.obtener_por_id(
            factura.cliente_id,
        )

        nombre_cliente = ""

        if cliente is not None:

            nombre_cliente = (
                cliente.razon_social
                or cliente.nombre_completo
                or cliente.numero_documento
                or ""
            )

        self._factura = factura
        self._detalles = list(
            factura.detalles,
        )
        self._nombre_cliente = nombre_cliente

        self.lbl_titulo.setText(
            f"Factura {factura.numero}"
            + (
                f" — {nombre_cliente}"
                if nombre_cliente
                else ""
            ),
        )

        self._sincronizar_combo_formato()
        self._actualizar_vista_previa()
        self._actualizar_botones()

    def _imprimir(
        self,
    ) -> None:

        if self._factura is None:

            return

        imprimir_factura_venta(
            self._factura,
            self._detalles,
            self._nombre_cliente,
            parent=self,
            formato=self._formato_actual(),
        )

    def _exportar_pdf(
        self,
    ) -> None:

        if self._factura is None:

            return

        exportar_pdf_factura_venta(
            self._factura,
            self._detalles,
            self._nombre_cliente,
            parent=self,
            formato=self._formato_actual(),
        )
