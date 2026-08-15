from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.base.page import Page
from aplicacion.framework.ui.card import Card
from aplicacion.modulos.ventas.pos.servicios import (
    ServicioPOSVenta,
)
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


class POSCajaPage(Page):

    titulo = "Caja POS"

    icono = "ventas"

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "POSCajaPage",
        )

        habilitar_fondo_qss(
            self,
        )

        self._construir()

        self._consultar()

    def _construir(
        self,
    ) -> None:

        contenedor = QWidget()
        layout = QVBoxLayout(
            contenedor,
        )
        layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        card = Card(
            "Resumen de caja",
        )

        filtros = QWidget()
        fila = QGridLayout(
            filtros,
        )

        fila.addWidget(
            QLabel("Fecha:"),
            0,
            0,
        )

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(
            True,
        )
        self.fecha.setDate(
            QDate.currentDate(),
        )

        fila.addWidget(
            self.fecha,
            0,
            1,
        )

        btn_consultar = QPushButton(
            "Actualizar",
        )
        btn_consultar.clicked.connect(
            self._consultar,
        )

        fila.addWidget(
            btn_consultar,
            0,
            2,
        )

        card.contenido.addWidget(
            filtros,
        )

        metricas = QGridLayout()

        self.lbl_ventas = self._crear_metrica(
            "Ventas",
            "0",
        )
        self.lbl_total = self._crear_metrica(
            "Total vendido",
            "$0",
        )
        self.lbl_recibido = self._crear_metrica(
            "Recibido",
            "$0",
        )
        self.lbl_cambio = self._crear_metrica(
            "Cambio entregado",
            "$0",
        )

        metricas.addWidget(
            self.lbl_ventas[
                "contenedor"
            ],
            0,
            0,
        )
        metricas.addWidget(
            self.lbl_total[
                "contenedor"
            ],
            0,
            1,
        )
        metricas.addWidget(
            self.lbl_recibido[
                "contenedor"
            ],
            1,
            0,
        )
        metricas.addWidget(
            self.lbl_cambio[
                "contenedor"
            ],
            1,
            1,
        )

        card.contenido.addLayout(
            metricas,
        )

        self.lbl_metodos = QLabel(
            "Desglose por método de pago",
        )
        self.lbl_metodos.setStyleSheet(
            "font-weight:600;color:#1B4F8A;",
        )

        card.contenido.addWidget(
            self.lbl_metodos,
        )

        self.lbl_detalle_metodos = QLabel(
            "Sin ventas registradas.",
        )
        self.lbl_detalle_metodos.setWordWrap(
            True,
        )

        card.contenido.addWidget(
            self.lbl_detalle_metodos,
        )

        card_cierre = Card(
            "Arqueo y cierre de caja",
        )

        arqueo = QGridLayout()

        arqueo.addWidget(
            QLabel(
                "Efectivo esperado:",
            ),
            0,
            0,
        )

        self.lbl_efectivo_esperado = QLabel(
            "$0",
        )
        self.lbl_efectivo_esperado.setStyleSheet(
            "font-size:18px;font-weight:700;color:#111827;",
        )

        arqueo.addWidget(
            self.lbl_efectivo_esperado,
            0,
            1,
        )

        arqueo.addWidget(
            QLabel(
                "Efectivo contado:",
            ),
            1,
            0,
        )

        self.efectivo_contado = QDoubleSpinBox()
        self.efectivo_contado.setRange(
            0,
            999999999,
        )
        self.efectivo_contado.setDecimals(
            0,
        )
        self.efectivo_contado.valueChanged.connect(
            self._actualizar_diferencia,
        )

        arqueo.addWidget(
            self.efectivo_contado,
            1,
            1,
        )

        arqueo.addWidget(
            QLabel(
                "Diferencia:",
            ),
            2,
            0,
        )

        self.lbl_diferencia = QLabel(
            "$0",
        )
        self.lbl_diferencia.setStyleSheet(
            "font-size:16px;font-weight:600;color:#92400E;",
        )

        arqueo.addWidget(
            self.lbl_diferencia,
            2,
            1,
        )

        arqueo.addWidget(
            QLabel(
                "Observaciones:",
            ),
            3,
            0,
        )

        self.observaciones = QLineEdit()
        self.observaciones.setPlaceholderText(
            "Notas del arqueo (opcional)",
        )

        arqueo.addWidget(
            self.observaciones,
            3,
            1,
        )

        card_cierre.contenido.addLayout(
            arqueo,
        )

        self.lbl_estado_cierre = QLabel(
            "",
        )
        self.lbl_estado_cierre.setWordWrap(
            True,
        )

        card_cierre.contenido.addWidget(
            self.lbl_estado_cierre,
        )

        self.btn_cerrar = QPushButton(
            "Cerrar caja",
        )
        self.btn_cerrar.clicked.connect(
            self._cerrar_caja,
        )

        card_cierre.contenido.addWidget(
            self.btn_cerrar,
        )

        layout.addWidget(
            card,
        )
        layout.addWidget(
            card_cierre,
        )

        self.agregar_widget(
            contenedor,
            stretch=1,
        )

    def _crear_metrica(
        self,
        titulo: str,
        valor: str,
    ) -> dict:

        contenedor = QWidget()
        layout = QVBoxLayout(
            contenedor,
        )

        etiqueta = QLabel(
            titulo,
        )
        etiqueta.setStyleSheet(
            "color:#6B7280;font-size:12px;",
        )

        monto = QLabel(
            valor,
        )
        monto.setStyleSheet(
            "font-size:24px;font-weight:700;color:#111827;",
        )

        layout.addWidget(
            etiqueta,
        )
        layout.addWidget(
            monto,
        )

        return {
            "contenedor": contenedor,
            "valor": monto,
        }

    def _consultar(
        self,
    ) -> None:

        resumen = ServicioPOSVenta.resumen_caja(
            fecha=self.fecha.date().toPython(),
        )

        self.lbl_ventas[
            "valor"
        ].setText(
            str(
                resumen.get(
                    "ventas",
                    0,
                ),
            ),
        )

        self.lbl_total[
            "valor"
        ].setText(
            f"${float(resumen.get('total') or 0):,.0f}",
        )

        self.lbl_recibido[
            "valor"
        ].setText(
            f"${float(resumen.get('recibido') or 0):,.0f}",
        )

        self.lbl_cambio[
            "valor"
        ].setText(
            f"${float(resumen.get('cambio') or 0):,.0f}",
        )

        lineas = []

        for item in resumen.get(
            "por_metodo",
            [],
        ):

            metodo = str(
                item.get(
                    "metodo_pago",
                    "",
                )
                or "",
            ).replace(
                "_",
                " ",
            ).title()

            lineas.append(
                (
                    f"{metodo}: {item.get('ventas', 0)} ventas — "
                    f"${float(item.get('total') or 0):,.0f}"
                ),
            )

        if lineas:

            self.lbl_detalle_metodos.setText(
                "\n".join(
                    lineas,
                ),
            )

        else:

            self.lbl_detalle_metodos.setText(
                "Sin ventas registradas.",
            )

        esperado = ServicioPOSVenta.efectivo_esperado(
            fecha=self.fecha.date().toPython(),
        )

        self.lbl_efectivo_esperado.setText(
            f"${esperado:,.0f}",
        )

        self._actualizar_diferencia()

        cierre = ServicioPOSVenta.obtener_cierre(
            fecha=self.fecha.date().toPython(),
        )

        if cierre:

            self.lbl_estado_cierre.setText(
                (
                    f"Caja cerrada el "
                    f"{cierre['fecha_cierre'].strftime('%Y-%m-%d %H:%M')} "
                    f"por {cierre['usuario']}. "
                    f"Contado: ${cierre['efectivo_contado']:,.0f} — "
                    f"Diferencia: ${cierre['diferencia']:,.0f}"
                ),
            )
            self.efectivo_contado.setValue(
                cierre["efectivo_contado"],
            )
            self.observaciones.setText(
                str(
                    cierre.get(
                        "observaciones",
                    )
                    or "",
                ),
            )
            self.btn_cerrar.setEnabled(
                False,
            )
            self.efectivo_contado.setEnabled(
                False,
            )
            self.observaciones.setEnabled(
                False,
            )

        else:

            self.lbl_estado_cierre.setText(
                "La caja del día aún no ha sido cerrada.",
            )
            self.btn_cerrar.setEnabled(
                True,
            )
            self.efectivo_contado.setEnabled(
                True,
            )
            self.observaciones.setEnabled(
                True,
            )

    def _actualizar_diferencia(
        self,
    ) -> None:

        esperado = ServicioPOSVenta.efectivo_esperado(
            fecha=self.fecha.date().toPython(),
        )

        contado = float(
            self.efectivo_contado.value(),
        )

        diferencia = contado - esperado

        color = "#065F46"

        if abs(
            diferencia,
        ) > 0.01:

            color = "#B91C1C"

        self.lbl_diferencia.setText(
            f"${diferencia:,.0f}",
        )
        self.lbl_diferencia.setStyleSheet(
            f"font-size:16px;font-weight:600;color:{color};",
        )

    def _cerrar_caja(
        self,
    ) -> None:

        respuesta = QMessageBox.question(
            self,
            "Cierre de caja",
            "¿Confirma el cierre de caja con el efectivo contado?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if (
            respuesta
            != QMessageBox.StandardButton.Yes
        ):

            return

        try:

            cierre = ServicioPOSVenta.cerrar_caja(
                efectivo_contado=float(
                    self.efectivo_contado.value(),
                ),
                fecha=self.fecha.date().toPython(),
                observaciones=self.observaciones.text().strip()
                or None,
            )

            QMessageBox.information(
                self,
                "Cierre de caja",
                (
                    f"Caja cerrada correctamente.\n"
                    f"Diferencia: ${cierre['diferencia']:,.0f}"
                ),
            )

            self._consultar()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cierre de caja",
                str(
                    error,
                ),
            )
