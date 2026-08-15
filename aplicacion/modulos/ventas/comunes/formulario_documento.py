from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
)

from aplicacion.framework.base.page import Page
from aplicacion.maestros.impuestos.servicios import (
    ServicioImpuesto,
)
from aplicacion.modulos.ventas.cotizaciones.formulario import (
    FormularioCotizacion,
)


class FormularioDocumentoVenta(
    FormularioCotizacion,
):

    servicio_generador = None

    datasource_cls = None

    mensaje_guardado = "Documento guardado correctamente."

    ancho = 1160

    alto = 680

    def __init__(
        self,
        id_registro=None,
        parent=None,
    ):

        self.id_registro = id_registro

        self.es_edicion = (
            id_registro is not None
        )

        self.datasource = self.datasource_cls()

        self._cargando_registro = False

        ServicioImpuesto.inicializar_predeterminados()

        Page.__init__(
            self,
            parent,
        )

    def _crear_ui(
        self,
    ):

        FormularioCotizacion._crear_ui(
            self,
        )

        self._adaptar_interfaz_documento()

    def _adaptar_interfaz_documento(
        self,
    ):

        if (
            not self.es_edicion
            and self.servicio_generador is not None
        ):

            self.txt_numero.setText(
                self.servicio_generador.generar_numero(),
            )

        self.formato.hide()

        for etiqueta in self.findChildren(
            QLabel,
        ):

            if etiqueta.text() == "Formato impresión":

                etiqueta.hide()

        self.celda_retefuente.hide()
        self.celda_reteica.hide()
        self.celda_reteiva.hide()
        self.lbl_valor_retefuente.hide()
        self.lbl_valor_reteiva.hide()
        self.lbl_valor_reteica.hide()

        for etiqueta in self.findChildren(
            QLabel,
        ):

            if etiqueta.text() in (
                "Retefuente:",
                "ReteICA:",
                "ReteIVA:",
            ):

                etiqueta.hide()

        self.btn_imprimir.hide()
        self.btn_pdf.hide()
        self.btn_whatsapp.hide()
        self.btn_correo.hide()

    def _obtener_cabecera(
        self,
    ) -> dict:

        return {
            "numero": self.txt_numero.text().strip(),
            "fecha": self.fecha.date().toPython(),
            "cliente_id": self.cliente.valor(),
            "observaciones": self.observaciones.toPlainText().strip(),
            "vendedor": self.vendedor.text().strip(),
        }

    def _cargar_registro(
        self,
    ):

        registro = self.datasource.obtener_completa(
            self.id_registro,
        )

        if registro is None:

            return

        self._cargando_registro = True

        self.txt_numero.setText(
            registro.numero,
        )

        self.fecha.setDate(
            registro.fecha,
        )

        self.cliente.setValue(
            registro.cliente_id,
        )

        self.observaciones.setPlainText(
            str(
                registro.observaciones or "",
            ).strip(),
        )

        self.vendedor.setText(
            str(
                getattr(
                    registro,
                    "vendedor",
                    "",
                )
                or "",
            ).strip(),
        )

        self.tabla.setRowCount(
            0,
        )

        for detalle in registro.detalles:

            producto = None

            if detalle.producto_id:

                from aplicacion.maestros.productos.servicios import (
                    ServicioProducto,
                )

                producto = ServicioProducto.obtener_por_id(
                    detalle.producto_id,
                )

            codigo = ""
            nombre = detalle.descripcion or ""

            if producto is not None:

                codigo = producto.codigo or ""
                nombre = producto.nombre or nombre

            elif " - " in nombre:

                partes = nombre.split(
                    " - ",
                    1,
                )

                codigo = partes[0]
                nombre = partes[1]

            self._agregar_linea(
                producto_id=detalle.producto_id,
                producto_variante_id=getattr(
                    detalle,
                    "producto_variante_id",
                    None,
                ),
                codigo=codigo,
                nombre=nombre,
                cantidad=detalle.cantidad,
                precio=detalle.precio_unitario,
                impuesto_id=detalle.impuesto_id,
                precio_incluye_iva=bool(
                    getattr(
                        detalle,
                        "precio_incluye_iva",
                        False,
                    ),
                ),
            )

        self._recalcular_totales()

        self._cargando_registro = False

    def guardar(
        self,
    ):

        try:

            registro = self.datasource.guardar_completa(
                self._obtener_cabecera(),
                self._obtener_lineas(),
                self.id_registro,
            )

            self.id_registro = registro.id

            self.es_edicion = True

            self.txt_numero.setText(
                registro.numero,
            )

            QMessageBox.information(
                self,
                "Información",
                self.mensaje_guardado,
            )

            self.guardado.emit()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                str(error),
            )
