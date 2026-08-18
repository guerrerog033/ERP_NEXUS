from __future__ import annotations

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QValueAxis,
)
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from aplicacion.interfaz.kpis_inicio import (
    formatear_moneda,
)

_MESES_ABREV = (
    "",
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
)


def _texto_variacion(valor: float | None) -> str:

    if valor is None:

        return ""

    flecha = "▲" if valor >= 0 else "▼"

    return f"{flecha} {abs(valor):.1f}% vs periodo anterior"


from aplicacion.modulos.gerencial.servicios import (
    ServicioPanelGerencial,
)
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


class KpiCard(
    QFrame,
):

    clicked = Signal()

    def __init__(
        self,
        titulo: str,
        valor: str,
        *,
        detalle: str = "",
        clickeable: bool = False,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "PanelGerencialKpi",
        )

        if clickeable:

            self.setCursor(
                Qt.CursorShape.PointingHandCursor,
            )

        caja = QVBoxLayout(
            self,
        )

        lbl_titulo = QLabel(
            titulo,
        )
        lbl_titulo.setObjectName(
            "PanelGerencialKpiTitulo",
        )

        lbl_valor = QLabel(
            valor,
        )
        lbl_valor.setObjectName(
            "PanelGerencialKpiValor",
        )

        caja.addWidget(
            lbl_titulo,
        )
        caja.addWidget(
            lbl_valor,
        )

        if detalle:

            lbl_detalle = QLabel(
                detalle,
            )
            lbl_detalle.setWordWrap(
                True,
            )
            lbl_detalle.setObjectName(
                "PanelGerencialKpiDetalle",
            )
            caja.addWidget(
                lbl_detalle,
            )

        self._clickeable = clickeable

    def mouseReleaseEvent(
        self,
        event,
    ):

        if (
            self._clickeable
            and event.button()
            == Qt.MouseButton.LeftButton
        ):

            self.clicked.emit()

        super().mouseReleaseEvent(
            event,
        )


class PanelGerencialPage(QWidget):

    titulo = "Panel gerencial"

    icono = "contabilidad"

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "PanelGerencialPage",
        )

        habilitar_fondo_qss(
            self,
        )

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        self.lbl_empresa = QLabel()
        self.lbl_empresa.setObjectName(
            "PanelGerencialEmpresa",
        )

        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(
            True,
        )
        self.fecha_desde.setDate(
            QDate.currentDate().addDays(
                1
                - QDate.currentDate().day(),
            ),
        )

        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(
            True,
        )
        self.fecha_hasta.setDate(
            QDate.currentDate(),
        )

        btn_actualizar = QPushButton(
            "Actualizar",
        )
        btn_actualizar.clicked.connect(
            self._cargar_datos,
        )

        barra = QHBoxLayout()
        barra.addWidget(
            self.lbl_empresa,
            1,
        )
        barra.addWidget(
            QLabel(
                "Desde:",
            ),
        )
        barra.addWidget(
            self.fecha_desde,
        )
        barra.addWidget(
            QLabel(
                "Hasta:",
            ),
        )
        barra.addWidget(
            self.fecha_hasta,
        )
        barra.addWidget(
            btn_actualizar,
        )
        layout.addLayout(
            barra,
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(
            True,
        )
        scroll.setFrameShape(
            QFrame.Shape.NoFrame,
        )

        contenedor = QWidget()
        self.grid = QGridLayout(
            contenedor,
        )
        self.grid.setSpacing(
            12,
        )

        scroll.setWidget(
            contenedor,
        )
        layout.addWidget(
            scroll,
            1,
        )

        self._cargar_datos()

    def _abrir_modulo(
        self,
        modulo_id: str,
    ) -> None:

        from aplicacion.framework.app_context import (
            AppContext,
        )

        dashboard = getattr(
            AppContext,
            "dashboard",
            None,
        )

        if dashboard is not None:

            dashboard.modulo_seleccionado(
                modulo_id,
            )

    def _limpiar_grid(
        self,
    ) -> None:

        while self.grid.count():

            item = self.grid.takeAt(
                0,
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

    def _agregar_kpi(
        self,
        fila: int,
        col: int,
        titulo: str,
        valor: str,
        *,
        detalle: str = "",
        modulo_id: str | None = None,
    ) -> None:

        tarjeta = KpiCard(
            titulo,
            valor,
            detalle=detalle,
            clickeable=bool(
                modulo_id,
            ),
        )

        if modulo_id:

            tarjeta.clicked.connect(
                lambda _checked=False,
                mid=modulo_id: self._abrir_modulo(
                    mid,
                ),
            )

        self.grid.addWidget(
            tarjeta,
            fila,
            col,
        )

    def _cargar_datos(
        self,
    ) -> None:

        resumen = ServicioPanelGerencial.resumen(
            fecha_desde=self.fecha_desde.date().toPython(),
            fecha_hasta=self.fecha_hasta.date().toPython(),
        )
        pipeline = resumen.get(
            "pipeline_periodo",
            {},
        )
        etapas = pipeline.get(
            "etapas",
            {},
        )
        variacion = resumen.get(
            "variacion_periodo_anterior",
            {},
        )

        periodo = (
            f"{resumen.get('periodo_desde')} — "
            f"{resumen.get('periodo_hasta')}"
        )

        self.lbl_empresa.setText(
            f"{resumen.get('empresa') or 'Panel gerencial'}"
            f"  ·  {periodo}"
        )

        self._limpiar_grid()

        fila = 0
        col = 0

        tarjetas = [
            (
                "Ventas hoy",
                formatear_moneda(
                    float(
                        resumen.get(
                            "ventas_dia",
                            0,
                        )
                        or 0,
                    ),
                ),
                "",
                "ReporteVentas",
            ),
            (
                "Compras hoy",
                formatear_moneda(
                    float(
                        resumen.get(
                            "compras_dia",
                            0,
                        )
                        or 0,
                    ),
                ),
                "",
                "ReporteCompras",
            ),
            (
                "Utilidad estimada hoy",
                formatear_moneda(
                    float(
                        resumen.get(
                            "utilidad_estimada",
                            0,
                        )
                        or 0,
                    ),
                ),
                "Ventas − compras del día",
                None,
            ),
            (
                "CxC total",
                formatear_moneda(
                    float(
                        resumen.get(
                            "cxc_total",
                            0,
                        )
                        or 0,
                    ),
                ),
                (
                    "Vencido: "
                    + formatear_moneda(
                        float(
                            resumen.get(
                                "cxc_vencido",
                                0,
                            )
                            or 0,
                        ),
                    )
                ),
                "CarteraCxC",
            ),
            (
                "CxP total",
                formatear_moneda(
                    float(
                        resumen.get(
                            "cxp_total",
                            0,
                        )
                        or 0,
                    ),
                ),
                "",
                "CarteraCxP",
            ),
            (
                "Productos activos",
                str(
                    int(
                        resumen.get(
                            "productos_activos",
                            0,
                        )
                        or 0,
                    ),
                ),
                "",
                "Productos",
            ),
            (
                "Pipeline periodo",
                str(
                    pipeline.get(
                        "cotizaciones",
                        0,
                    ),
                )
                + " cotizaciones",
                (
                    "Cobrado: "
                    + formatear_moneda(
                        float(
                            pipeline.get(
                                "total_cobrado",
                                0,
                            )
                            or 0,
                        ),
                    )
                    + "  "
                    + _texto_variacion(
                        variacion.get("cobrado"),
                    )
                ),
                "ReportePipelineComercial",
            ),
            (
                "Cotizado periodo",
                formatear_moneda(
                    float(
                        pipeline.get(
                            "total_cotizado",
                            0,
                        )
                        or 0,
                    ),
                ),
                _texto_variacion(
                    variacion.get("cotizado"),
                ),
                "ReportePipelineComercial",
            ),
        ]

        for titulo, valor, detalle, modulo_id in tarjetas:

            self._agregar_kpi(
                fila,
                col,
                titulo,
                valor,
                detalle=detalle,
                modulo_id=modulo_id,
            )

            col += 1

            if col > 2:

                col = 0
                fila += 1

        fila += 1

        embudo = QFrame()
        embudo.setObjectName(
            "PanelGerencialEmbudo",
        )
        layout_embudo = QVBoxLayout(
            embudo,
        )

        titulo_embudo = QLabel(
            "Embudo comercial (periodo seleccionado)",
        )
        titulo_embudo.setObjectName(
            "PanelGerencialEmbudoTitulo",
        )
        layout_embudo.addWidget(
            titulo_embudo,
        )

        orden_etapas = (
            "cotización",
            "pedido",
            "remisión",
            "factura",
            "cobrado",
        )

        max_total = max(
            (
                float(
                    etapas.get(
                        etapa,
                        {},
                    ).get(
                        "total",
                        0,
                    )
                    or 0,
                )
                for etapa in orden_etapas
            ),
            default=0.0,
        )

        if max_total <= 0:

            max_total = 1.0

        for etapa in orden_etapas:

            datos = etapas.get(
                etapa,
                {},
            )

            cantidad = int(
                datos.get(
                    "cantidad",
                    0,
                )
                or 0,
            )

            total = float(
                datos.get(
                    "total",
                    0,
                )
                or 0,
            )

            barra = QProgressBar()
            barra.setObjectName(
                "PanelGerencialEmbudoBarra",
            )
            barra.setRange(
                0,
                100,
            )
            barra.setValue(
                int(
                    total
                    / max_total
                    * 100,
                ),
            )
            barra.setFormat(
                f"{etapa.capitalize()}: "
                f"{cantidad} · "
                f"{formatear_moneda(total)}"
            )

            layout_embudo.addWidget(
                barra,
            )

        self.grid.addWidget(
            embudo,
            fila,
            0,
            1,
            3,
        )

        fila += 1

        top_productos = resumen.get(
            "top_productos",
            [],
        )

        self.grid.addWidget(
            self._construir_top_productos(
                top_productos,
            ),
            fila,
            0,
            1,
            3,
        )

        fila += 1

        serie_mensual = resumen.get(
            "serie_mensual",
            [],
        )

        grafico = self._construir_grafico_mensual(
            serie_mensual,
        )

        if grafico is not None:

            self.grid.addWidget(
                grafico,
                fila,
                0,
                1,
                3,
            )

    def _construir_top_productos(
        self,
        top_productos: list,
    ) -> QFrame:

        marco = QFrame()
        marco.setObjectName(
            "PanelGerencialEmbudo",
        )
        layout = QVBoxLayout(marco)

        titulo = QLabel(
            "Productos más vendidos (periodo seleccionado)",
        )
        titulo.setObjectName(
            "PanelGerencialEmbudoTitulo",
        )
        layout.addWidget(titulo)

        if not top_productos:

            layout.addWidget(
                QLabel(
                    "Sin ventas registradas en el periodo.",
                ),
            )

            return marco

        tabla = QTableWidget(
            len(top_productos),
            3,
        )
        tabla.setHorizontalHeaderLabels(
            ["Producto", "Cantidad", "Valor vendido"],
        )
        tabla.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers,
        )

        for fila_idx, producto in enumerate(top_productos):

            tabla.setItem(
                fila_idx,
                0,
                QTableWidgetItem(
                    str(producto.get("nombre", "")),
                ),
            )
            tabla.setItem(
                fila_idx,
                1,
                QTableWidgetItem(
                    f"{float(producto.get('cantidad', 0) or 0):,.0f}",
                ),
            )
            tabla.setItem(
                fila_idx,
                2,
                QTableWidgetItem(
                    formatear_moneda(
                        float(
                            producto.get("valor", 0) or 0,
                        ),
                    ),
                ),
            )

        tabla.setMaximumHeight(
            32 * (len(top_productos) + 1),
        )
        layout.addWidget(tabla)

        return marco

    def _construir_grafico_mensual(
        self,
        serie_mensual: list,
    ):

        if not serie_mensual:

            return None

        set_ventas = QBarSet("Ventas")
        set_compras = QBarSet("Compras")

        categorias = []

        for punto in serie_mensual:

            set_ventas.append(
                float(punto.get("ventas", 0) or 0),
            )
            set_compras.append(
                float(punto.get("compras", 0) or 0),
            )
            categorias.append(
                _MESES_ABREV[int(punto.get("mes", 0))]
                + " "
                + str(punto.get("anio", ""))[-2:]
            )

        series = QBarSeries()
        series.append(set_ventas)
        series.append(set_compras)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(
            "Ventas vs. compras (últimos meses)",
        )
        chart.legend().setVisible(True)

        eje_x = QBarCategoryAxis()
        eje_x.append(categorias)
        chart.addAxis(
            eje_x,
            Qt.AlignmentFlag.AlignBottom,
        )
        series.attachAxis(eje_x)

        eje_y = QValueAxis()
        chart.addAxis(
            eje_y,
            Qt.AlignmentFlag.AlignLeft,
        )
        series.attachAxis(eje_y)

        vista_grafico = QChartView(chart)
        vista_grafico.setRenderHint(
            QPainter.RenderHint.Antialiasing,
        )
        vista_grafico.setMinimumHeight(260)

        return vista_grafico
