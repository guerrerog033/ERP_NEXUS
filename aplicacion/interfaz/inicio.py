from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from aplicacion.interfaz.kpis_inicio import (
    formatear_moneda,
    obtener_resumen_inicio,
)
from aplicacion.framework.menu_manifest import (
    modulo_accesible,
)
from aplicacion.nucleo.configuracion import Configuracion


def accesos_rapidos_visibles() -> list[
    tuple[
        str,
        str,
    ]
]:

    return [
        (
            titulo,
            modulo_id,
        )
        for titulo, modulo_id in ACCESOS_RAPIDOS
        if modulo_accesible(
            modulo_id,
        )
    ]


ACCESOS_RAPIDOS = [

    (
        "Cotizaciones",
        "Cotizaciones",
    ),

    (
        "Pedidos",
        "Pedidos",
    ),

    (
        "Clientes",
        "Clientes",
    ),

    (
        "Productos",
        "Productos",
    ),

    (
        "Empresas",
        "Empresas",
    ),

    (
        "Cartera",
        "Cartera",
    ),

    (
        "Reportes",
        "Reportes",
    ),

    (
        "Compras",
        "Compras",
    ),

]


class Tarjeta(QFrame):

    def __init__(
        self,
        titulo: str,
        valor: str = "—",
        detalle: str = "",
    ):

        super().__init__()

        self.setObjectName(
            "TarjetaInicio",
        )

        self.setFrameShape(
            QFrame.StyledPanel,
        )

        layout = QVBoxLayout(
            self,
        )

        layout.setSpacing(
            4,
        )

        self.lbl_titulo = QLabel(
            titulo,
        )

        self.lbl_titulo.setAlignment(
            Qt.AlignCenter,
        )

        self.lbl_titulo.setObjectName(
            "TarjetaInicioTitulo",
        )

        self.lbl_valor = QLabel(
            valor,
        )

        self.lbl_valor.setAlignment(
            Qt.AlignCenter,
        )

        self.lbl_valor.setObjectName(
            "TarjetaInicioValor",
        )

        layout.addWidget(
            self.lbl_titulo,
        )

        layout.addWidget(
            self.lbl_valor,
        )

        self.lbl_detalle = QLabel(
            detalle,
        )

        self.lbl_detalle.setObjectName(
            "TarjetaInicioDetalle",
        )

        self.lbl_detalle.setAlignment(
            Qt.AlignCenter,
        )

        self.lbl_detalle.setVisible(
            bool(
                detalle,
            ),
        )

        layout.addWidget(
            self.lbl_detalle,
        )

    def actualizar(
        self,
        valor: str,
        detalle: str = "",
    ) -> None:

        self.lbl_valor.setText(
            valor,
        )

        self.lbl_detalle.setText(
            detalle,
        )

        self.lbl_detalle.setVisible(
            bool(
                detalle,
            ),
        )


class Inicio(QWidget):

    modulo_solicitado = Signal(
        str,
    )

    def __init__(
        self,
    ):

        super().__init__()

        self.setObjectName(
            "Inicio",
        )

        principal = QVBoxLayout(
            self,
        )

        principal.setContentsMargins(
            24,
            20,
            24,
            20,
        )

        scroll = QScrollArea()

        scroll.setObjectName(
            "InicioScroll",
        )

        scroll.setWidgetResizable(
            True,
        )

        scroll.setFrameShape(
            QFrame.NoFrame,
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff,
        )

        panel = QFrame()

        panel.setObjectName(
            "PanelInicio",
        )

        self._panel_layout = QVBoxLayout(
            panel,
        )

        self._panel_layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        nombre_erp = (
            Configuracion.obtener(
                "erp",
                "nombre",
            )
            or "ERP NEXUS"
        )

        self.lbl_titulo = QLabel(
            nombre_erp,
        )

        self.lbl_titulo.setAlignment(
            Qt.AlignLeft,
        )

        self.lbl_titulo.setObjectName(
            "InicioTitulo",
        )

        self.lbl_subtitulo = QLabel()

        self.lbl_subtitulo.setAlignment(
            Qt.AlignLeft,
        )

        self.lbl_subtitulo.setObjectName(
            "InicioSubtitulo",
        )

        self._panel_layout.addWidget(
            self.lbl_titulo,
        )

        self._panel_layout.addWidget(
            self.lbl_subtitulo,
        )

        self._panel_layout.addSpacing(
            20,
        )

        grid = QGridLayout()

        grid.setSpacing(
            16,
        )

        self.tarjeta_hoy = Tarjeta(
            "Cotizaciones hoy",
        )

        self.tarjeta_mes = Tarjeta(
            "Cotizaciones del mes",
        )

        self.tarjeta_productos = Tarjeta(
            "Por cobrar (CxC)",
        )

        self.tarjeta_clientes = Tarjeta(
            "Por pagar (CxP)",
        )

        self.tarjeta_vencido = Tarjeta(
            "CxC vencido",
        )

        self.tarjeta_maestros_clientes = Tarjeta(
            "Clientes activos",
        )

        self.tarjeta_maestros_productos = Tarjeta(
            "Productos activos",
        )

        grid.addWidget(
            self.tarjeta_hoy,
            0,
            0,
        )

        grid.addWidget(
            self.tarjeta_mes,
            0,
            1,
        )

        grid.addWidget(
            self.tarjeta_maestros_clientes,
            0,
            2,
        )

        grid.addWidget(
            self.tarjeta_productos,
            1,
            0,
        )

        grid.addWidget(
            self.tarjeta_clientes,
            1,
            1,
        )

        grid.addWidget(
            self.tarjeta_vencido,
            1,
            2,
        )

        grid.addWidget(
            self.tarjeta_maestros_productos,
            2,
            0,
        )

        self._panel_layout.addLayout(
            grid,
        )

        self._panel_layout.addSpacing(
            24,
        )

        etiqueta_accesos = QLabel(
            "Accesos rápidos",
        )

        etiqueta_accesos.setObjectName(
            "InicioSeccionTitulo",
        )

        self._panel_layout.addWidget(
            etiqueta_accesos,
        )

        accesos_layout = QHBoxLayout()

        accesos_layout.setSpacing(
            10,
        )

        for etiqueta, modulo_id in accesos_rapidos_visibles():

            boton = QPushButton(
                etiqueta,
            )

            boton.setObjectName(
                "BotonAccesoRapido",
            )

            boton.setCursor(
                Qt.PointingHandCursor,
            )

            boton.clicked.connect(

                lambda _checked=False,
                nombre=modulo_id: self._abrir_modulo(
                    nombre,
                ),

            )

            accesos_layout.addWidget(
                boton,
            )

        accesos_layout.addStretch()

        self._panel_layout.addLayout(
            accesos_layout,
        )

        self._panel_layout.addSpacing(
            20,
        )

        self.lbl_recientes_titulo = QLabel(
            "Últimas cotizaciones",
        )

        self.lbl_recientes_titulo.setObjectName(
            "InicioSeccionTitulo",
        )

        self._contenedor_recientes = QFrame()

        self._contenedor_recientes.setObjectName(
            "InicioListaRecientes",
        )

        self._layout_recientes = QVBoxLayout(
            self._contenedor_recientes,
        )

        self._layout_recientes.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self._layout_recientes.setSpacing(
            0,
        )

        self._panel_layout.addWidget(
            self.lbl_recientes_titulo,
        )

        self._panel_layout.addWidget(
            self._contenedor_recientes,
        )

        self._panel_layout.addStretch()

        scroll.setWidget(
            panel,
        )

        principal.addWidget(
            scroll,
        )

        self.actualizar()

    def _abrir_modulo(
        self,
        modulo_id: str,
    ) -> None:

        self.modulo_solicitado.emit(
            modulo_id,
        )

    def actualizar(
        self,
    ) -> None:

        resumen = obtener_resumen_inicio()

        if resumen.empresa_nombre:

            self.lbl_subtitulo.setText(
                f"Bienvenido — {resumen.empresa_nombre}",
            )

        else:

            self.lbl_subtitulo.setText(
                "Bienvenido al sistema de gestión empresarial",
            )

        detalle_hoy = (
            f"{resumen.cotizaciones_hoy_cantidad} "
            f"{'cotización' if resumen.cotizaciones_hoy_cantidad == 1 else 'cotizaciones'}"
        )

        self.tarjeta_hoy.actualizar(
            formatear_moneda(
                resumen.cotizaciones_hoy_total,
            ),
            detalle_hoy,
        )

        detalle_mes = (
            formatear_moneda(
                resumen.cotizaciones_mes_total,
            )
            + " acumulado"
        )

        self.tarjeta_mes.actualizar(
            str(
                resumen.cotizaciones_mes_cantidad,
            ),
            detalle_mes,
        )

        self.tarjeta_productos.actualizar(
            formatear_moneda(
                resumen.cxc_total,
            ),
        )

        self.tarjeta_clientes.actualizar(
            formatear_moneda(
                resumen.cxp_total,
            ),
        )

        self.tarjeta_vencido.actualizar(
            formatear_moneda(
                resumen.cxc_vencido,
            ),
            "Cartera vencida",
        )

        self.tarjeta_maestros_clientes.actualizar(
            str(
                resumen.clientes_activos,
            ),
            "Terceros clientes",
        )

        self.tarjeta_maestros_productos.actualizar(
            str(
                resumen.productos_activos,
            ),
            "Referencia en inventario",
        )

        self._actualizar_recientes(
            resumen.recientes,
        )

    def _actualizar_recientes(
        self,
        recientes,
    ) -> None:

        while self._layout_recientes.count():

            item = self._layout_recientes.takeAt(
                0,
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

        if not recientes:

            vacio = QLabel(
                "Aún no hay cotizaciones registradas.",
            )

            vacio.setObjectName(
                "InicioListaVacia",
            )

            self._layout_recientes.addWidget(
                vacio,
            )

            return

        for item in recientes:

            fila = QPushButton()

            fila.setObjectName(
                "InicioFilaReciente",
            )

            fila.setCursor(
                Qt.PointingHandCursor,
            )

            fila.setText(
                f"{item.numero}   ·   "
                f"{item.fecha.strftime('%d/%m/%Y')}   ·   "
                f"{formatear_moneda(item.total)}",
            )

            fila.clicked.connect(

                lambda _checked=False,
                _id=item.id: self._abrir_modulo(
                    "Cotizaciones",
                ),

            )

            self._layout_recientes.addWidget(
                fila,
            )
