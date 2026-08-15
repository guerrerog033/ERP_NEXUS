from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
)

from aplicacion.framework.ui.inquiry_page import (
    InquiryPage,
)
from aplicacion.modulos.ventas.pos.servicios import (
    ServicioPOSVenta,
)


class POSHistorialPage(
    InquiryPage,
):

    titulo = "Historial POS"

    icono = "ventas"

    _NOMBRE_EXPORT = "historial_pos"

    _COLUMNAS = [
        "Fecha",
        "Factura",
        "Total",
        "Recibido",
        "Cambio",
        "Pago",
        "Usuario",
    ]

    def _crear_filtros(
        self,
    ) -> None:

        self._layout_filtros.addWidget(
            QLabel("Desde:"),
        )

        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(
            True,
        )
        self.fecha_desde.setDate(
            QDate.currentDate().addDays(
                -7,
            ),
        )

        self._layout_filtros.addWidget(
            self.fecha_desde,
        )

        self._layout_filtros.addWidget(
            QLabel("Hasta:"),
        )

        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(
            True,
        )
        self.fecha_hasta.setDate(
            QDate.currentDate(),
        )

        self._layout_filtros.addWidget(
            self.fecha_hasta,
        )

        self._layout_filtros.addWidget(
            QLabel("Pago:"),
        )

        self.metodo_pago = QComboBox()
        self.metodo_pago.addItem(
            "Todos",
            None,
        )
        self.metodo_pago.addItem(
            "Efectivo",
            "efectivo",
        )
        self.metodo_pago.addItem(
            "Tarjeta",
            "tarjeta",
        )
        self.metodo_pago.addItem(
            "Transferencia",
            "transferencia",
        )

        self._layout_filtros.addWidget(
            self.metodo_pago,
        )

        self._layout_filtros.addWidget(
            QLabel("Usuario:"),
        )

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText(
            "Cajero",
        )
        self.usuario.setMaximumWidth(
            140,
        )

        self._layout_filtros.addWidget(
            self.usuario,
        )

    def _agregar_botones_filtro(
        self,
    ) -> None:

        btn_reimprimir = QPushButton(
            "Reimprimir ticket",
        )
        btn_reimprimir.clicked.connect(
            self._reimprimir_ticket,
        )

        btn_devolver = QPushButton(
            "Devolver venta",
        )
        btn_devolver.clicked.connect(
            self._devolver_venta,
        )

        btn_cartera = QPushButton(
            "Cartera cliente",
        )
        btn_cartera.clicked.connect(
            self._ver_cartera_cliente,
        )

        btn_estado = QPushButton(
            "Estado de cuenta",
        )
        btn_estado.clicked.connect(
            self._ver_estado_cuenta_cliente,
        )

        self._layout_filtros.addWidget(
            btn_reimprimir,
        )
        self._layout_filtros.addWidget(
            btn_devolver,
        )
        self._layout_filtros.addWidget(
            btn_cartera,
        )
        self._layout_filtros.addWidget(
            btn_estado,
        )

    def _registro_seleccionado(
        self,
    ) -> dict | None:

        fila = self.tabla.currentRow()

        if fila < 0:

            QMessageBox.warning(
                self,
                "Historial POS",
                "Seleccione una venta de la tabla.",
            )

            return None

        item = self.tabla.item(
            fila,
            0,
        )

        log_id = item.data(
            Qt.ItemDataRole.UserRole,
        )

        if not log_id:

            QMessageBox.warning(
                self,
                "Historial POS",
                "No se pudo identificar la venta.",
            )

            return None

        cliente_id = item.data(
            Qt.ItemDataRole.UserRole
            + 1,
        )

        return {
            "log_id": int(
                log_id,
            ),
            "cliente_id": cliente_id,
        }

    def _ver_cartera_cliente(
        self,
    ) -> None:

        registro = self._registro_seleccionado()

        if registro is None:

            return

        from aplicacion.modulos.cartera.ui_comercial import (
            mostrar_cartera_cliente,
        )

        mostrar_cartera_cliente(
            self,
            registro.get(
                "cliente_id",
            ),
        )

    def _ver_estado_cuenta_cliente(
        self,
    ) -> None:

        registro = self._registro_seleccionado()

        if registro is None:

            return

        from aplicacion.modulos.cartera.ui_comercial import (
            mostrar_estado_cuenta_cliente,
        )

        mostrar_estado_cuenta_cliente(
            self,
            registro.get(
                "cliente_id",
            ),
        )

    def _devolver_venta(
        self,
    ) -> None:

        registro = self._registro_seleccionado()

        if registro is None:

            return

        log_id = registro["log_id"]

        confirmar = QMessageBox.question(
            self,
            "Devolver venta",
            "Se generará una nota crédito por el total "
            "de la factura y se revertirá inventario. "
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

            nota = ServicioPOSVenta.devolver_venta(
                log_id=int(
                    log_id,
                ),
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Devolver venta",
                str(
                    error,
                ),
            )

            return

        QMessageBox.information(
            self,
            "Devolver venta",
            f"Nota crédito {nota.numero} generada.",
        )

        self._consultar()

    def _reimprimir_ticket(
        self,
    ) -> None:

        registro = self._registro_seleccionado()

        if registro is None:

            return

        log_id = registro["log_id"]

        try:

            ServicioPOSVenta.reimprimir_ticket(
                int(
                    log_id,
                ),
                parent=self,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Historial POS",
                str(
                    error,
                ),
            )

    def _consultar(
        self,
    ) -> None:

        registros = ServicioPOSVenta.listar_historial(
            fecha_desde=self.fecha_desde.date().toPython(),
            fecha_hasta=self.fecha_hasta.date().toPython(),
            metodo_pago=self.metodo_pago.currentData(),
            usuario=self.usuario.text().strip()
            or None,
        )

        self.tabla.setRowCount(
            len(
                registros,
            ),
        )

        for fila, registro in enumerate(
            registros,
        ):

            fecha = registro.get(
                "fecha",
            )

            texto_fecha = ""

            if fecha is not None:

                texto_fecha = fecha.strftime(
                    "%Y-%m-%d %H:%M",
                )

            valores = [
                texto_fecha,
                str(
                    registro.get(
                        "factura_numero",
                        "",
                    )
                    or "",
                ),
                f"${float(registro.get('total') or 0):,.0f}",
                f"${float(registro.get('recibido') or 0):,.0f}",
                f"${float(registro.get('cambio') or 0):,.0f}",
                str(
                    registro.get(
                        "metodo_pago",
                        "",
                    )
                    or "",
                ).replace(
                    "_",
                    " ",
                ).title(),
                str(
                    registro.get(
                        "usuario",
                        "",
                    )
                    or "",
                ),
            ]

            for columna, valor in enumerate(
                valores,
            ):

                item = QTableWidgetItem(
                    valor,
                )

                if columna in {
                    2,
                    3,
                    4,
                }:

                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter,
                    )

                if columna == 0:

                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        registro.get(
                            "id",
                        ),
                    )
                    item.setData(
                        Qt.ItemDataRole.UserRole
                        + 1,
                        registro.get(
                            "cliente_id",
                        ),
                    )

                self.tabla.setItem(
                    fila,
                    columna,
                    item,
                )
