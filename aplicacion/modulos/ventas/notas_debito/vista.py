from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from aplicacion.framework.ui.vista_documento import (
    VistaDocumento,
    mostrar_dialogo_vista,
)
from aplicacion.maestros.terceros.servicio import (
    TerceroServicio,
)
from aplicacion.modulos.ventas.notas_debito.datasource import (
    NotaDebitoVentaDataSource,
)


class VistaNotaDebitoVenta(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = NotaDebitoVentaDataSource()

        self._nota = None

        self._nombre_cliente = ""

        super().__init__(
            id_registro,
            parent=parent,
        )

    def _agregar_barras_accion(
        self,
    ) -> None:

        self.btn_emitir = self.boton_accion(
            "Emitir ND DIAN",
        )

        self.btn_confirmar = self.boton_accion(
            "Confirmar",
        )

        self.btn_contabilizar = self.boton_accion(
            "Contabilizar",
        )

        self.btn_factura_origen = self.boton_accion(
            "Ver factura",
        )

        self.btn_cartera = self.boton_accion(
            "Cartera cliente",
        )

        self.btn_estado_cuenta = self.boton_accion(
            "Estado de cuenta",
        )

        self.btn_cerrar = self.boton_accion(
            "Cerrar",
        )

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Nota débito",
                (
                    self.btn_confirmar,
                    self.btn_emitir,
                    self.btn_contabilizar,
                    self.btn_factura_origen,
                    self.btn_cartera,
                    self.btn_estado_cuenta,
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

        self.btn_confirmar.clicked.connect(
            self._confirmar_generacion,
        )

        self.btn_contabilizar.clicked.connect(
            self._contabilizar,
        )

        self.btn_factura_origen.clicked.connect(
            self._ver_factura_origen,
        )

        self.btn_cartera.clicked.connect(
            self._ver_cartera_cliente,
        )

        self.btn_estado_cuenta.clicked.connect(
            self._ver_estado_cuenta_cliente,
        )

        self.btn_cerrar.clicked.connect(
            self.cerrar.emit,
        )

    def _actualizar_botones(
        self,
    ) -> None:

        if self._nota is None:

            return

        self.btn_emitir.setEnabled(
            self._nota.estado
            not in (
                "emitida",
                "contabilizada",
            )
        )

        self.btn_confirmar.setEnabled(
            self._nota.estado
            == "borrador",
        )

        self.btn_contabilizar.setEnabled(
            not self._nota.contabilizado
            and self._nota.estado
            not in (
                "borrador",
            )
        )

        self.btn_factura_origen.setEnabled(
            bool(
                self._nota.factura_id,
            ),
        )

    def _emitir_dian(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Emitir nota débito",
            "Se generará el XML y se enviará a la DIAN. "
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

    def _confirmar_generacion(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Confirmar nota débito",
            "Se aplicará el efecto comercial "
            "(saldo y contabilidad según configuración) "
            "sin enviar a la DIAN. "
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

            nota = self.datasource.confirmar_generacion(
                self.id_registro,
                emitir_dian=False,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Confirmar nota débito",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Confirmar nota débito",
            f"Nota {nota.numero} confirmada.",
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
            "esta nota débito. "
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

    def _ver_factura_origen(
        self,
    ) -> None:

        if (
            self._nota is None
            or not self._nota.factura_id
        ):

            QMessageBox.warning(
                self,
                "Ver factura",
                "No hay factura de referencia.",
            )

            return

        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )
        from aplicacion.modulos.ventas.facturas.vista_factura import (
            VistaFacturaVenta,
        )

        factura = ServicioFacturaVenta.obtener_completa(
            self._nota.factura_id,
        )

        if factura is None:

            QMessageBox.warning(
                self,
                "Ver factura",
                "No se encontró la factura referenciada.",
            )

            return

        mostrar_dialogo_vista(
            VistaFacturaVenta,
            factura.id,
            titulo=f"Factura {factura.numero}",
            parent=self,
        )

    def _ver_cartera_cliente(
        self,
    ) -> None:

        from aplicacion.modulos.cartera.ui_comercial import (
            cartera_desde_documento,
        )

        cartera_desde_documento(
            self,
            self._nota,
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
            self._nota,
            nombre_cliente=self._nombre_cliente,
        )

    def _cargar_datos(
        self,
    ) -> None:

        nota = self.datasource.obtener_completa(
            self.id_registro,
        )

        if nota is None:

            QMessageBox.warning(
                self,
                "Nota débito",
                "No se encontró la nota débito.",
            )

            self.cerrar.emit()

            return

        cliente = TerceroServicio.obtener_por_id(
            nota.cliente_id,
        )

        nombre_cliente = ""

        if cliente is not None:

            nombre_cliente = (
                cliente.razon_social
                or cliente.nombre_completo
                or cliente.numero_documento
                or ""
            )

        self._nota = nota

        self._nombre_cliente = nombre_cliente

        titulo = f"Nota débito {nota.numero}"

        if nombre_cliente:

            titulo = (
                f"{titulo} — {nombre_cliente}"
            )

        self.lbl_titulo.setText(
            titulo,
        )

        estado = [
            nota.estado,
        ]

        if nota.estado_dian:

            estado.append(
                nota.estado_dian,
            )

        if nota.motivo:

            estado.append(
                nota.motivo,
            )

        self.mostrar_formato(
            " · ".join(estado),
        )

        filas = ""

        for detalle in nota.detalles:

            filas += (
                "<tr>"
                f"<td>{detalle.descripcion}</td>"
                f"<td align='right'>{detalle.cantidad:.2f}</td>"
                f"<td align='right'>${detalle.total_linea:,.2f}</td>"
                "</tr>"
            )

        html = (
            "<h2>Nota débito de venta</h2>"
            f"<p><b>Factura referencia:</b> "
            f"{nota.factura_id}</p>"
            f"<p><b>CUFE factura:</b> "
            f"{nota.factura_cufe or '-'}</p>"
            f"<p><b>Subtotal:</b> ${nota.subtotal:,.2f}<br>"
            f"<b>IVA:</b> ${nota.iva:,.2f}<br>"
            f"<b>Total:</b> ${nota.total:,.2f}</p>"
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

    def _imprimir(
        self,
    ) -> None:

        if self._nota is None:

            return

        from aplicacion.modulos.ventas.notas_debito.impresion import (
            imprimir_nota_debito_venta,
        )

        imprimir_nota_debito_venta(
            self._nota,
            list(
                self._nota.detalles,
            ),
            self._nombre_cliente,
            parent=self,
        )

    def _exportar_pdf(
        self,
    ) -> None:

        if self._nota is None:

            return

        from aplicacion.modulos.ventas.notas_debito.impresion import (
            exportar_pdf_nota_debito_venta,
        )

        exportar_pdf_nota_debito_venta(
            self._nota,
            list(
                self._nota.detalles,
            ),
            self._nombre_cliente,
            parent=self,
        )
