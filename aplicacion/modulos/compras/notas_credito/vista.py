from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from aplicacion.framework.ui.vista_documento import (
    VistaDocumento,
)
from aplicacion.maestros.terceros.servicio import (
    TerceroServicio,
)
from aplicacion.modulos.compras.notas_credito.datasource import (
    NotaCreditoCompraDataSource,
)


class VistaNotaCreditoCompra(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = NotaCreditoCompraDataSource()

        self._nota = None

        super().__init__(
            id_registro,
            parent=parent,
        )

    def _agregar_barras_accion(
        self,
    ) -> None:

        self.btn_aplicar = self.boton_accion(
            "Aplicar devolución",
        )

        self.btn_cerrar = self.boton_accion(
            "Cerrar",
        )

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Nota crédito compra",
                (
                    self.btn_aplicar,
                    self.btn_cerrar,
                ),
                separar_ultimo=True,
            ),
        )

    def _conectar_acciones(
        self,
    ) -> None:

        self.btn_aplicar.clicked.connect(
            self._aplicar,
        )

        self.btn_cerrar.clicked.connect(
            self.cerrar.emit,
        )

    def _actualizar_botones(
        self,
    ) -> None:

        if self._nota is None:

            return

        self.btn_aplicar.setEnabled(
            self._nota.estado != "aplicada",
        )

    def _aplicar(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Aplicar devolución",
            "Se registrará salida de inventario, "
            "asiento contable y reducción de CxP. "
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

            asiento = self.datasource.aplicar(
                self.id_registro,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Aplicar devolución",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Aplicar devolución",
            f"Asiento {asiento.numero} registrado.",
        )

        self._cargar_datos()

        self.actualizado.emit()

    def _cargar_datos(
        self,
    ) -> None:

        nota = self.datasource.obtener_completa(
            self.id_registro,
        )

        if nota is None:

            QMessageBox.warning(
                self,
                "Nota crédito compra",
                "No se encontró la nota crédito.",
            )

            self.cerrar.emit()

            return

        proveedor = TerceroServicio.obtener_por_id(
            nota.proveedor_id,
        )

        nombre = ""

        if proveedor is not None:

            nombre = (
                proveedor.razon_social
                or proveedor.nombre_comercial
                or proveedor.nombre_completo
                or ""
            )

        self._nota = nota

        titulo = f"NC compra {nota.numero}"

        if nombre:

            titulo = f"{titulo} — {nombre}"

        self.lbl_titulo.setText(
            titulo,
        )

        estado = [
            nota.estado,
        ]

        if nota.motivo:

            estado.append(
                nota.motivo,
            )

        if nota.contabilizado:

            estado.append(
                "Contabilizada",
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
            "<h2>Nota crédito de compra</h2>"
            f"<p><b>Factura referencia:</b> "
            f"{nota.factura_compra_id}</p>"
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
