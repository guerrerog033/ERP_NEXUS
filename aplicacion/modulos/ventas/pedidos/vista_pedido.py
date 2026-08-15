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
from aplicacion.modulos.ventas.facturas.integracion import (
    IntegracionFacturaVenta,
)
from aplicacion.modulos.ventas.pedidos.datasource import (
    PedidoDataSource,
)
from aplicacion.modulos.ventas.pedidos.formatos_impresion import (
    generar_html_pedido,
)
from aplicacion.modulos.ventas.pedidos.impresion import (
    exportar_pdf_pedido,
    imprimir_pedido,
)
from aplicacion.modulos.ventas.remisiones.servicios import (
    ServicioRemision,
)
from aplicacion.modulos.ventas.remisiones.vista_remision import (
    VistaRemision,
)
from aplicacion.recursos.ui.botones import Botones


class VistaPedido(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = PedidoDataSource()

        self._pedido = None
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

        self.btn_facturar = self.boton_accion(
            "Facturar",
        )

        self.btn_remisionar = self.boton_accion(
            "Remisionar",
        )

        self.btn_reservar = self.boton_accion(
            "Reservar stock",
        )

        self.btn_liberar_reserva = self.boton_accion(
            "Liberar reserva",
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
                    self.btn_facturar,
                    self.btn_remisionar,
                    self.btn_reservar,
                    self.btn_liberar_reserva,
                    self.btn_cartera,
                    self.btn_estado_cuenta,
                ),
            ),
        )

        self.btn_editar = Botones.editar()

        self.btn_editar.setVisible(
            False,
        )

        self.btn_imprimir = Botones.editar()

        self.btn_imprimir.setText(
            "Imprimir",
        )

        self.btn_pdf = Botones.aceptar()

        self.btn_pdf.setText(
            "PDF",
        )

        self.btn_cerrar = Botones.cerrar()

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
            self._confirmar_pedido,
        )

        self.btn_facturar.clicked.connect(
            self._facturar,
        )

        self.btn_remisionar.clicked.connect(
            self._remisionar,
        )

        self.btn_reservar.clicked.connect(
            self._reservar_stock,
        )

        self.btn_liberar_reserva.clicked.connect(
            self._liberar_reserva,
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

        return "Pedido"

    def _facturar(
        self,
    ) -> None:

        if self._pedido is None:

            return

        IntegracionFacturaVenta.iniciar_facturacion_desde_pedido(
            self.id_registro,
            self,
        )

    def _remisionar(
        self,
    ) -> None:

        if self._pedido is None:

            return

        try:

            remision = ServicioRemision.crear_desde_pedido(
                self.id_registro,
            )

        except ValueError as error:

            existente = ServicioRemision.repositorio.obtener_por_pedido(
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

    def _actualizar_botones(
        self,
    ) -> None:

        if self._pedido is None:

            return

        from aplicacion.modulos.ventas.pedidos.reservas import (
            ServicioReservaPedido,
        )

        reserva_habilitada = (
            ServicioReservaPedido.reserva_habilitada()
        )

        operativo = (
            self._pedido.estado != "borrador"
        )

        self.btn_confirmar.setEnabled(
            self._pedido.estado == "borrador",
        )

        self.btn_facturar.setEnabled(
            operativo,
        )

        self.btn_remisionar.setEnabled(
            operativo,
        )

        self.btn_reservar.setVisible(
            reserva_habilitada,
        )

        self.btn_liberar_reserva.setVisible(
            reserva_habilitada,
        )

        self.btn_reservar.setEnabled(
            operativo
            and reserva_habilitada
            and not self._pedido.reserva_aplicada,
        )

        self.btn_liberar_reserva.setEnabled(
            operativo
            and reserva_habilitada
            and self._pedido.reserva_aplicada,
        )

    def _confirmar_pedido(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Confirmar pedido",
            "El pedido quedará listo para remisionar, "
            "facturar o reservar stock. "
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

            pedido = self.datasource.confirmar_pedido(
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Confirmar pedido",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Confirmar pedido",
            f"Pedido {pedido.numero} confirmado.",
        )

        self._cargar_datos()
        self.actualizado.emit()

    def _reservar_stock(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Reservar stock",
            "Se apartará inventario para este pedido. "
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

            self.datasource.reservar_inventario(
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Reservar stock",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Reservar stock",
            "Reserva registrada correctamente.",
        )

        self._cargar_datos()
        self.actualizado.emit()

    def _liberar_reserva(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Liberar reserva",
            "Se liberará el stock reservado. "
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

            self.datasource.liberar_reserva(
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Liberar reserva",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Liberar reserva",
            "Reserva liberada.",
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
            self._pedido,
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
            self._pedido,
            nombre_cliente=self._nombre_cliente,
        )

    def _cargar_datos(
        self,
    ) -> None:

        pedido = self.datasource.obtener_completa(
            self.id_registro,
        )

        if pedido is None:

            QMessageBox.warning(
                self,
                "Pedido",
                "No se encontró el pedido seleccionado.",
            )

            self.cerrar.emit()

            return

        cliente = TerceroServicio.obtener_por_id(
            pedido.cliente_id,
        )

        nombre_cliente = ""

        if cliente is not None:

            nombre_cliente = (
                cliente.razon_social
                or cliente.nombre_completo
                or cliente.numero_documento
                or ""
            )

        self._pedido = pedido
        self._detalles = list(
            pedido.detalles,
        )
        self._nombre_cliente = nombre_cliente
        self._cliente = cliente

        self.lbl_titulo.setText(
            f"Pedido {pedido.numero}"
            + (
                f" — {nombre_cliente}"
                if nombre_cliente
                else ""
            ),
        )

        self.mostrar_formato(
            f"Estado: {pedido.estado}",
        )

        self.establecer_html(
            generar_html_pedido(
                pedido,
                self._detalles,
                nombre_cliente,
            ),
        )

        self._actualizar_botones()

    def _imprimir(
        self,
    ) -> None:

        if self._pedido is None:

            return

        imprimir_pedido(
            self._pedido,
            self._detalles,
            self._nombre_cliente,
            parent=self,
            cliente=self._cliente,
        )

    def _exportar_pdf(
        self,
    ) -> None:

        if self._pedido is None:

            return

        exportar_pdf_pedido(
            self._pedido,
            self._detalles,
            self._nombre_cliente,
            parent=self,
            cliente=self._cliente,
        )
