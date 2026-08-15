from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from aplicacion.framework.ui.vista_documento import (
    VistaDocumento,
)
from aplicacion.maestros.terceros.servicio import (
    TerceroServicio,
)
from aplicacion.modulos.ventas.facturas.integracion import (
    IntegracionFacturaVenta,
)
from aplicacion.modulos.ventas.remisiones.datasource import (
    RemisionDataSource,
)
from aplicacion.modulos.ventas.remisiones.formatos_impresion import (
    generar_html_remision,
)
from aplicacion.modulos.ventas.remisiones.impresion import (
    exportar_pdf_remision,
    imprimir_remision,
)


class VistaRemision(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = RemisionDataSource()

        self._remision = None
        self._detalles: list = []
        self._nombre_cliente = ""
        self._cliente = None

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

        self.btn_despachar = self.boton_accion(
            "Despachar",
        )

        self.btn_facturar = self.boton_accion(
            "Facturar",
        )

        self.btn_guia_electronica = self.boton_accion(
            "Guía electrónica",
        )

        self.btn_ver_guia = self.boton_accion(
            "Ver guía DIAN",
        )

        self.btn_marcar_entregado = self.boton_accion(
            "Marcar entregado",
        )

        self.btn_cartera = self.boton_accion(
            "Cartera cliente",
        )

        self.btn_estado_cuenta = self.boton_accion(
            "Estado de cuenta",
        )

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Documento interno",
                (
                    self.btn_confirmar,
                    self.btn_facturar,
                    self.btn_despachar,
                    self.btn_guia_electronica,
                    self.btn_ver_guia,
                    self.btn_marcar_entregado,
                    self.btn_cartera,
                    self.btn_estado_cuenta,
                ),
            ),
        )

        self.btn_editar = self.boton_accion(
            "Editar",
        )

        self.btn_editar.setVisible(
            False,
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
            self._confirmar_remision,
        )

        self.btn_despachar.clicked.connect(
            self._despachar,
        )

        self.btn_guia_electronica.clicked.connect(
            self._crear_guia_electronica,
        )

        self.btn_ver_guia.clicked.connect(
            self._ver_guia_electronica,
        )

        self.btn_marcar_entregado.clicked.connect(
            self._marcar_entregado,
        )

        self.btn_facturar.clicked.connect(
            self._facturar,
        )

        self.btn_cartera.clicked.connect(
            self._ver_cartera_cliente,
        )

        self.btn_estado_cuenta.clicked.connect(
            self._ver_estado_cuenta_cliente,
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

        return "Remisión interna"

    def _actualizar_botones(
        self,
    ) -> None:

        if self._remision is None:

            return

        self.btn_confirmar.setEnabled(
            self._remision.estado == "borrador",
        )

        operativa = (
            self._remision.estado != "borrador"
        )

        self.btn_despachar.setEnabled(
            operativa
            and not self._remision.inventario_aplicado,
        )

        self.btn_facturar.setEnabled(
            operativa,
        )

        from aplicacion.modulos.ventas.guias_remision.servicios import (
            ServicioGuiaRemisionElectronica,
        )

        guia = ServicioGuiaRemisionElectronica.obtener_por_remision(
            self.id_registro,
        )

        tiene_guia = guia is not None
        guia_emitida = (
            ServicioGuiaRemisionElectronica
            .guia_emitida_para_remision(
                self.id_registro,
            )
        )

        self.btn_guia_electronica.setEnabled(
            not tiene_guia,
        )

        self.btn_ver_guia.setVisible(
            tiene_guia,
        )

        self.btn_ver_guia.setEnabled(
            tiene_guia,
        )

        entregada = (
            self._remision.estado == "entregada"
        )

        puede_entregar = (
            self._remision.inventario_aplicado
            and not entregada
            and (
                guia_emitida
                or not ServicioGuiaRemisionElectronica
                .exigir_guia_emitida_logistica()
            )
        )

        self.btn_marcar_entregado.setVisible(
            self._remision.inventario_aplicado,
        )

        self.btn_marcar_entregado.setEnabled(
            puede_entregar,
        )

        if (
            self._remision.inventario_aplicado
            and not entregada
            and ServicioGuiaRemisionElectronica
            .exigir_guia_emitida_logistica()
            and not guia_emitida
        ):

            self.btn_marcar_entregado.setToolTip(
                "Requiere guía electrónica emitida DIAN.",
            )

        else:

            self.btn_marcar_entregado.setToolTip(
                "",
            )

    def _facturar(
        self,
    ) -> None:

        if self._remision is None:

            return

        IntegracionFacturaVenta.iniciar_facturacion_desde_remision(
            self.id_registro,
            self,
        )

    def _confirmar_remision(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Confirmar remisión",
            "La remisión quedará lista para despacho "
            "o facturación. ¿Desea continuar?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if (
            confirmar
            != QMessageBox.StandardButton.Yes
        ):

            return

        try:

            remision = self.datasource.confirmar_remision(
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Confirmar remisión",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Confirmar remisión",
            f"Remisión {remision.numero} confirmada.",
        )

        self._cargar_datos()
        self.actualizado.emit()

    def _despachar(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Despachar",
            "Se registrará la salida de inventario. "
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

            self.datasource.despachar(
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Despachar",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Despachar",
            "Remisión despachada e inventario actualizado.",
        )

        self._cargar_datos()
        self.actualizado.emit()

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

        from PySide6.QtWidgets import (
            QDialogButtonBox,
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

    def _crear_guia_electronica(
        self,
    ) -> None:

        from aplicacion.modulos.ventas.guias_remision.servicios import (
            ServicioGuiaRemisionElectronica,
        )
        from aplicacion.modulos.ventas.guias_remision.vista import (
            VistaGuiaRemisionElectronica,
        )

        transporte = self._solicitar_transporte()

        if transporte is None:

            return

        try:

            guia = (
                ServicioGuiaRemisionElectronica
                .crear_desde_remision(
                    self.id_registro,
                    **transporte,
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Guía electrónica",
                str(error),
            )

            return

        ventana = QDialog(
            self,
        )

        ventana.setWindowTitle(
            f"Guía {guia.numero}",
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

        vista = VistaGuiaRemisionElectronica(
            id_registro=guia.id,
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

        self._cargar_datos()
        self.actualizado.emit()

    def _ver_guia_electronica(
        self,
    ) -> None:

        from aplicacion.modulos.ventas.guias_remision.servicios import (
            ServicioGuiaRemisionElectronica,
        )
        from aplicacion.modulos.ventas.guias_remision.vista import (
            VistaGuiaRemisionElectronica,
        )

        guia = ServicioGuiaRemisionElectronica.obtener_por_remision(
            self.id_registro,
        )

        if guia is None:

            QMessageBox.information(
                self,
                "Guía electrónica",
                "Esta remisión no tiene guía electrónica.",
            )

            return

        ventana = QDialog(
            self,
        )

        ventana.setWindowTitle(
            f"Guía {guia.numero}",
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

        vista = VistaGuiaRemisionElectronica(
            id_registro=guia.id,
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

        self._cargar_datos()
        self.actualizado.emit()

    def _marcar_entregado(
        self,
    ) -> None:

        from aplicacion.modulos.logistica.despacho.servicios import (
            ServicioDespacho,
        )

        confirmar = QMessageBox.question(
            self,
            "Marcar entregado",
            "Se registrará la entrega al cliente. "
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

            ServicioDespacho.marcar_entregado_por_remision(
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Marcar entregado",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Marcar entregado",
            "Entrega registrada correctamente.",
        )

        self._cargar_datos()
        self.actualizado.emit()

    def _ver_cartera_cliente(
        self,
    ) -> None:

        from aplicacion.modulos.cartera.ui_comercial import (
            cartera_desde_documento,
        )

        cartera_desde_documento(
            self,
            self._remision,
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
            self._remision,
            nombre_cliente=self._nombre_cliente,
        )

    def _cargar_datos(
        self,
    ) -> None:

        remision = self.datasource.obtener_completa(
            self.id_registro,
        )

        if remision is None:

            QMessageBox.warning(
                self,
                "Remisión interna",
                "No se encontró la remisión seleccionada.",
            )

            self.cerrar.emit()

            return

        cliente = TerceroServicio.obtener_por_id(
            remision.cliente_id,
        )

        nombre_cliente = ""

        if cliente is not None:

            nombre_cliente = (
                cliente.razon_social
                or cliente.nombre_completo
                or cliente.numero_documento
                or ""
            )

        self._remision = remision
        self._detalles = list(
            remision.detalles,
        )
        self._nombre_cliente = nombre_cliente
        self._cliente = cliente

        self.lbl_titulo.setText(
            f"Remisión interna {remision.numero}"
            + (
                f" — {nombre_cliente}"
                if nombre_cliente
                else ""
            ),
        )

        self.mostrar_formato(
            f"Estado: {remision.estado}",
        )

        self.establecer_html(
            generar_html_remision(
                remision,
                self._detalles,
                nombre_cliente,
            ),
        )

        self._actualizar_botones()

    def _imprimir(
        self,
    ) -> None:

        if self._remision is None:

            return

        imprimir_remision(
            self._remision,
            self._detalles,
            self._nombre_cliente,
            parent=self,
            cliente=self._cliente,
        )

    def _exportar_pdf(
        self,
    ) -> None:

        if self._remision is None:

            return

        exportar_pdf_remision(
            self._remision,
            self._detalles,
            self._nombre_cliente,
            parent=self,
            cliente=self._cliente,
        )
