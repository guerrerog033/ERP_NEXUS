from __future__ import annotations

from PySide6.QtWidgets import (
    QMessageBox,
)

from aplicacion.framework.ui.vista_documento import (
    VistaDocumento,
    mostrar_dialogo_vista,
)
from aplicacion.maestros.terceros.servicio import (
    TerceroServicio,
)
from aplicacion.modulos.ventas.cotizaciones.datasource import (
    CotizacionDataSource,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    etiqueta_formato,
    generar_html_cotizacion,
    normalizar_formato_codigo,
)
from aplicacion.modulos.ventas.cotizaciones.impresion import (
    enviar_correo_cotizacion,
    enviar_whatsapp_cotizacion,
    exportar_pdf_cotizacion,
    imprimir_cotizacion,
)
from aplicacion.modulos.ventas.facturas.integracion import (
    IntegracionFacturaVenta,
)
from aplicacion.modulos.ventas.pedidos.servicios import (
    ServicioPedido,
)
from aplicacion.modulos.ventas.pedidos.vista_pedido import (
    VistaPedido,
)
from aplicacion.modulos.ventas.remisiones.servicios import (
    ServicioRemision,
)
from aplicacion.modulos.ventas.remisiones.vista_remision import (
    VistaRemision,
)
from aplicacion.recursos.ui.botones import Botones


class VistaCotizacion(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = CotizacionDataSource()

        self._cotizacion = None
        self._detalles: list = []
        self._cliente = None
        self._nombre_cliente = ""

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

        self.btn_cartera = self.boton_accion(
            "Cartera cliente",
        )

        self.btn_estado_cuenta = self.boton_accion(
            "Estado de cuenta",
        )

        self.btn_facturar = self.boton_accion(
            "Facturar",
        )

        self.btn_remisionar = self.boton_accion(
            "Remisionar",
        )

        self.btn_orden_pedido = self.boton_accion(
            "Orden de pedido",
        )

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Documento",
                (
                    self.btn_confirmar,
                    self.btn_cartera,
                    self.btn_estado_cuenta,
                    self.btn_facturar,
                    self.btn_remisionar,
                    self.btn_orden_pedido,
                ),
            ),
        )

        self.btn_editar = Botones.editar()

        self.btn_imprimir = Botones.editar()

        self.btn_imprimir.setText(
            "Imprimir",
        )

        self.btn_pdf = Botones.aceptar()

        self.btn_pdf.setText(
            "PDF",
        )

        self.btn_whatsapp = Botones.nuevo()

        self.btn_whatsapp.setText(
            "WhatsApp",
        )

        self.btn_correo = Botones.buscar()

        self.btn_correo.setText(
            "Correo",
        )

        self.btn_cerrar = Botones.cerrar()

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Cotización",
                (
                    self.btn_editar,
                    self.btn_imprimir,
                    self.btn_pdf,
                    self.btn_whatsapp,
                    self.btn_correo,
                    self.btn_cerrar,
                ),
                separar_ultimo=True,
            ),
        )

    def _conectar_acciones(
        self,
    ) -> None:

        self.btn_editar.clicked.connect(
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

        self.btn_confirmar.clicked.connect(
            self._confirmar_cotizacion,
        )

        self.btn_cartera.clicked.connect(
            self._ver_cartera_cliente,
        )

        self.btn_estado_cuenta.clicked.connect(
            self._ver_estado_cuenta_cliente,
        )

        self.btn_facturar.clicked.connect(
            self._facturar,
        )

        self.btn_remisionar.clicked.connect(
            self._remisionar,
        )

        self.btn_orden_pedido.clicked.connect(
            self._crear_orden_pedido,
        )

        self.btn_whatsapp.clicked.connect(
            self._enviar_whatsapp,
        )

        self.btn_correo.clicked.connect(
            self._enviar_correo,
        )

    def etiqueta_barra_principal(
        self,
    ) -> str:

        return "Cotización"

    def _actualizar_botones(
        self,
    ) -> None:

        if self._cotizacion is None:

            return

        operativa = (
            self._cotizacion.estado != "borrador"
        )

        self.btn_confirmar.setEnabled(
            self._cotizacion.estado == "borrador",
        )

        self.btn_facturar.setEnabled(
            operativa,
        )

        self.btn_remisionar.setEnabled(
            operativa,
        )

        self.btn_orden_pedido.setEnabled(
            operativa,
        )

        editable = (
            str(
                self._cotizacion.estado or "",
            ).lower()
            == "borrador"
        )

        self.btn_editar.setVisible(
            editable,
        )

        self.btn_editar.setEnabled(
            editable,
        )

    def _confirmar_cotizacion(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Confirmar cotización",
            "La cotización quedará aprobada y lista "
            "para generar pedido, remisión o factura. "
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

            cotizacion = (
                self.datasource.confirmar_cotizacion(
                    self.id_registro,
                )
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Confirmar cotización",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Confirmar cotización",
            f"Cotización {cotizacion.numero} confirmada.",
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
            self._cotizacion,
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
            self._cotizacion,
            nombre_cliente=self._nombre_cliente,
        )

    def _facturar(
        self,
    ) -> None:

        if self._cotizacion is None:

            return

        IntegracionFacturaVenta.iniciar_facturacion_desde_cotizacion(
            self.id_registro,
            self,
        )

    def _remisionar(
        self,
    ) -> None:

        if self._cotizacion is None:

            return

        try:

            remision = ServicioRemision.crear_desde_cotizacion(
                self.id_registro,
            )

        except ValueError as error:

            existente = ServicioRemision.repositorio.obtener_por_cotizacion(
                self.id_registro,
            )

            if existente is not None:

                abrir = QMessageBox.question(
                    self,
                    "Remisionar",
                    f"{error}\n\n¿Desea abrir la remisión existente?",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                )

                if (
                    abrir
                    == QMessageBox.StandardButton.Yes
                ):

                    mostrar_dialogo_vista(
                        VistaRemision,
                        existente.id,
                        titulo=(
                            f"Remisión {existente.numero}"
                        ),
                        parent=self,
                    )

                return

            QMessageBox.warning(
                self,
                "Remisionar",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Remisionar",
            f"Se creó la remisión {remision.numero}.",
        )

        mostrar_dialogo_vista(
            VistaRemision,
            remision.id,
            titulo=f"Remisión {remision.numero}",
            parent=self,
        )

    def _crear_orden_pedido(
        self,
    ) -> None:

        if self._cotizacion is None:

            return

        try:

            pedido = ServicioPedido.crear_desde_cotizacion(
                self.id_registro,
            )

        except ValueError as error:

            existente = ServicioPedido.repositorio.obtener_por_cotizacion(
                self.id_registro,
            )

            if existente is not None:

                abrir = QMessageBox.question(
                    self,
                    "Orden de pedido",
                    f"{error}\n\n¿Desea abrir el pedido existente?",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                )

                if (
                    abrir
                    == QMessageBox.StandardButton.Yes
                ):

                    mostrar_dialogo_vista(
                        VistaPedido,
                        existente.id,
                        titulo=(
                            f"Pedido {existente.numero}"
                        ),
                        parent=self,
                    )

                return

            QMessageBox.warning(
                self,
                "Orden de pedido",
                str(
                    error,
                ),
            )

            return

        QMessageBox.information(
            self,
            "Orden de pedido",
            f"Se creó el pedido {pedido.numero}.",
        )

        mostrar_dialogo_vista(
            VistaPedido,
            pedido.id,
            titulo=f"Pedido {pedido.numero}",
            parent=self,
        )

    def _cargar_datos(
        self,
    ) -> None:

        cotizacion = self.datasource.obtener_completa(
            self.id_registro,
        )

        if cotizacion is None:

            QMessageBox.warning(
                self,
                "Cotización",
                "No se encontró la cotización seleccionada.",
            )

            self.cerrar.emit()

            return

        cliente = TerceroServicio.obtener_por_id(
            cotizacion.cliente_id,
        )

        nombre_cliente = ""

        if cliente is not None:

            nombre_cliente = (
                cliente.razon_social
                or cliente.nombre_completo
                or cliente.numero_documento
                or ""
            )

        self._cotizacion = cotizacion
        self._detalles = list(
            cotizacion.detalles,
        )
        self._cliente = cliente
        self._nombre_cliente = nombre_cliente

        formato = normalizar_formato_codigo(
            cotizacion.formato_impresion,
        )

        self.lbl_titulo.setText(
            f"Cotización {cotizacion.numero}"
            + (
                f" — {nombre_cliente}"
                if nombre_cliente
                else ""
            ),
        )

        self.mostrar_formato(
            f"Formato: {etiqueta_formato(formato)}",
        )

        self.establecer_html(
            generar_html_cotizacion(
                cotizacion,
                self._detalles,
                nombre_cliente,
            ),
        )

        self._actualizar_botones()

    def _imprimir(
        self,
    ) -> None:

        if self._cotizacion is None:

            return

        imprimir_cotizacion(
            self._cotizacion,
            self._detalles,
            self._nombre_cliente,
            parent=self,
        )

    def _exportar_pdf(
        self,
    ) -> None:

        if self._cotizacion is None:

            return

        exportar_pdf_cotizacion(
            self._cotizacion,
            self._detalles,
            self._nombre_cliente,
            parent=self,
        )

    def _enviar_whatsapp(
        self,
    ) -> None:

        if self._cotizacion is None:

            return

        enviar_whatsapp_cotizacion(
            self._cotizacion,
            self._detalles,
            self._nombre_cliente,
            cliente=self._cliente,
            parent=self,
        )

    def _enviar_correo(
        self,
    ) -> None:

        if self._cotizacion is None:

            return

        enviar_correo_cotizacion(
            self._cotizacion,
            self._detalles,
            self._nombre_cliente,
            cliente=self._cliente,
            parent=self,
        )
