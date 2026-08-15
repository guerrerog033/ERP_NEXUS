from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from aplicacion.modulos.contabilidad.procesos import (
    CUENTAS_CONTABLES,
    MAS_PROCESOS,
    MODULOS_ENLACE,
)
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


class HubContabilidad(QWidget):

    titulo = "Contabilidad"

    icono = "contabilidad"

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "HubContabilidad",
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

        layout.setSpacing(
            0,
        )

        self.tabs = QTabWidget()

        self.tabs.setObjectName(
            "ContabilidadTabs",
        )

        self.tabs.addTab(
            self._crear_tab(
                CUENTAS_CONTABLES,
            ),
            "Cuentas contables",
        )

        self.tabs.addTab(
            self._crear_tab(
                MAS_PROCESOS,
            ),
            "Más procesos",
        )

        self.tabs.setCurrentIndex(
            1,
        )

        layout.addWidget(
            self.tabs,
        )

    def _crear_tab(
        self,
        secciones: list[
            tuple[
                str,
                list[str],
            ]
        ],
    ) -> QWidget:

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
            secciones,
        ):

            fila = indice // 3

            columna = indice % 3

            grid.addWidget(
                self._crear_tarjeta(
                    titulo,
                    items,
                ),
                fila,
                columna,
            )

        for columna in range(
            3,
        ):

            grid.setColumnStretch(
                columna,
                1,
            )

        scroll.setWidget(
            contenedor,
        )

        return scroll

    def _crear_tarjeta(
        self,
        titulo: str,
        items: list[str],
    ) -> QFrame:

        tarjeta = QFrame()

        tarjeta.setObjectName(
            "TarjetaProcesoContabilidad",
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
            "TarjetaProcesoContabilidadTitulo",
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
                "EnlaceProcesoContabilidad",
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
            "Contabilidad",
            f"«{nombre}» estará disponible próximamente.",
        )
