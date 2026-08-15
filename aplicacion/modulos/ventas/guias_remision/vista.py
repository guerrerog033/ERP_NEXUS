from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from aplicacion.framework.ui.vista_documento import (
    VistaDocumento,
)
from aplicacion.maestros.terceros.servicio import (
    TerceroServicio,
)
from aplicacion.modulos.ventas.guias_remision.datasource import (
    GuiaRemisionElectronicaDataSource,
)


class VistaGuiaRemisionElectronica(VistaDocumento):

    def __init__(
        self,
        id_registro: int,
        parent=None,
    ):

        self.datasource = GuiaRemisionElectronicaDataSource()

        self._guia = None

        super().__init__(
            id_registro,
            parent=parent,
        )

    def _agregar_barras_accion(
        self,
    ) -> None:

        self.btn_emitir = self.boton_accion(
            "Emitir DIAN",
        )

        self.btn_cerrar = self.boton_accion(
            "Cerrar",
        )

        self.layout_principal.addLayout(
            self._barra_etiquetada(
                "Guía electrónica",
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

        if self._guia is None:

            return

        self.btn_emitir.setEnabled(
            self._guia.estado != "emitida",
        )

    def _emitir_dian(
        self,
    ) -> None:

        confirmar = QMessageBox.question(
            self,
            "Emitir guía DIAN",
            "Se generará el XML, firmará y enviará "
            "la guía de remisión electrónica. "
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
                "Emitir guía DIAN",
                str(error),
            )

            return

        if resultado.exito:

            QMessageBox.information(
                self,
                "Emitir guía DIAN",
                resultado.mensaje
                or "Guía emitida correctamente.",
            )

        else:

            QMessageBox.warning(
                self,
                "Emitir guía DIAN",
                resultado.error
                or resultado.mensaje
                or "No se pudo emitir la guía.",
            )

        self._cargar_datos()
        self.actualizado.emit()

    def _cargar_datos(
        self,
    ) -> None:

        guia = self.datasource.obtener_completa(
            self.id_registro,
        )

        if guia is None:

            QMessageBox.warning(
                self,
                "Guía electrónica",
                "No se encontró la guía.",
            )

            self.cerrar.emit()

            return

        cliente = TerceroServicio.obtener_por_id(
            guia.cliente_id,
        )

        nombre = ""

        if cliente is not None:

            nombre = (
                cliente.razon_social
                or cliente.nombre_completo
                or ""
            )

        self._guia = guia

        titulo = f"Guía {guia.numero}"

        if nombre:

            titulo = f"{titulo} — {nombre}"

        self.lbl_titulo.setText(
            titulo,
        )

        estado = [
            guia.estado,
        ]

        if guia.estado_dian:

            estado.append(
                guia.estado_dian,
            )

        if guia.remision_numero:

            estado.append(
                f"Rem. {guia.remision_numero}",
            )

        self.mostrar_formato(
            " · ".join(estado),
        )

        filas = ""

        for detalle in guia.detalles:

            filas += (
                "<tr>"
                f"<td>{detalle.descripcion}</td>"
                f"<td align='right'>{detalle.cantidad:.2f}</td>"
                "</tr>"
            )

        html = (
            "<h2>Guía de remisión electrónica</h2>"
            f"<p><b>Remisión interna:</b> "
            f"{guia.remision_numero or '—'}</p>"
            f"<p><b>CUDE:</b> {guia.cude or '—'}</p>"
            f"<p><b>Origen:</b> "
            f"{guia.direccion_origen or '—'} "
            f"({guia.ciudad_origen or ''})</p>"
            f"<p><b>Destino:</b> "
            f"{guia.direccion_destino or '—'} "
            f"({guia.ciudad_destino or ''})</p>"
            f"<p><b>Transporte:</b> "
            f"{guia.transportadora or '—'} · "
            f"{guia.conductor or '—'} · "
            f"{guia.placa or guia.vehiculo or '—'}</p>"
            "<table border='1' cellspacing='0' "
            "cellpadding='6' width='100%'>"
            "<tr><th>Descripción</th><th>Cant.</th></tr>"
            f"{filas}"
            "</table>"
        )

        self.establecer_html(
            html,
        )

        self._actualizar_botones()
