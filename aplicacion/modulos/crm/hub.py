from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from aplicacion.interfaz.kpis_inicio import (
    formatear_moneda,
)
from aplicacion.modulos.crm.procesos import (
    MODULOS_ENLACE,
    PROCESOS_CRM,
)
from aplicacion.modulos.crm.servicios import (
    ServicioCRM,
)
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


class HubCRM(QWidget):

    titulo = "CRM"

    icono = "terceros"

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "HubCRM",
        )

        habilitar_fondo_qss(
            self,
        )

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        resumen = ServicioCRM.resumen()

        panel_kpi = QFrame()

        panel_kpi.setObjectName(
            "PanelKpiCRM",
        )

        kpi_layout = QGridLayout(
            panel_kpi,
        )

        kpi_layout.addWidget(
            self._crear_kpi(
                "Oportunidades abiertas",
                str(
                    resumen["abiertas"],
                ),
            ),
            0,
            0,
        )

        kpi_layout.addWidget(
            self._crear_kpi(
                "Pipeline ponderado",
                formatear_moneda(
                    float(
                        resumen[
                            "valor_pipeline"
                        ],
                    ),
                ),
            ),
            0,
            1,
        )

        layout.addWidget(
            panel_kpi,
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True,
        )

        scroll.setFrameShape(
            QFrame.NoFrame,
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff,
        )

        contenedor = QWidget()

        grid = QGridLayout(
            contenedor,
        )

        grid.setContentsMargins(
            4,
            8,
            4,
            8,
        )

        grid.setSpacing(
            16,
        )

        for indice, (
            titulo,
            items,
        ) in enumerate(
            PROCESOS_CRM,
        ):

            fila = indice // 2
            columna = indice % 2

            grid.addWidget(
                self._crear_tarjeta(
                    titulo,
                    items,
                ),
                fila,
                columna,
            )

        for columna in range(
            2,
        ):

            grid.setColumnStretch(
                columna,
                1,
            )

        scroll.setWidget(
            contenedor,
        )

        layout.addWidget(
            scroll,
        )

    def _crear_kpi(
        self,
        titulo: str,
        valor: str,
    ) -> QFrame:

        marco = QFrame()

        marco_layout = QVBoxLayout(
            marco,
        )

        etiqueta = QLabel(
            titulo,
        )

        valor_lbl = QLabel(
            valor,
        )

        valor_lbl.setObjectName(
            "KpiValorCRM",
        )

        marco_layout.addWidget(
            etiqueta,
        )

        marco_layout.addWidget(
            valor_lbl,
        )

        return marco

    def _crear_tarjeta(
        self,
        titulo: str,
        items: list[str],
    ) -> QFrame:

        tarjeta = QFrame()

        tarjeta.setObjectName(
            "TarjetaProcesoCRM",
        )

        habilitar_fondo_qss(
            tarjeta,
        )

        layout = QVBoxLayout(
            tarjeta,
        )

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(
            6,
        )

        etiqueta = QLabel(
            titulo,
        )

        etiqueta.setObjectName(
            "TarjetaProcesoCRMTitulo",
        )

        layout.addWidget(
            etiqueta,
        )

        layout.addSpacing(
            4,
        )

        for item in items:

            boton = QPushButton(
                f"›  {item}",
            )

            boton.setObjectName(
                "EnlaceProcesoCRM",
            )

            boton.setCursor(
                Qt.PointingHandCursor,
            )

            boton.setFlat(
                True,
            )

            boton.clicked.connect(

                lambda _checked=False,
                nombre=item: self._abrir_proceso(
                    nombre,
                ),

            )

            layout.addWidget(
                boton,
            )

        layout.addStretch()

        return tarjeta

    def _abrir_proceso(
        self,
        nombre: str,
    ) -> None:

        modulo_id = MODULOS_ENLACE.get(
            nombre,
        )

        if modulo_id:

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

                return

        QMessageBox.information(
            self,
            "CRM",
            f"«{nombre}» estará disponible próximamente.",
        )
