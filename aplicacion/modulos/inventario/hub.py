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

from aplicacion.modulos.inventario.procesos import (
    MODULOS_ENLACE,
    PROCESOS_INVENTARIO,
)
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


class HubInventarios(QWidget):

    titulo = "Inventarios"

    icono = "productos"

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "HubInventarios",
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
            PROCESOS_INVENTARIO,
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

        layout.addWidget(
            scroll,
        )

    def _crear_tarjeta(
        self,
        titulo: str,
        items: list[str],
    ) -> QFrame:

        tarjeta = QFrame()

        tarjeta.setObjectName(
            "TarjetaProcesoInventario",
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
            "TarjetaProcesoInventarioTitulo",
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
                "EnlaceProcesoInventario",
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
            "Inventarios",
            f"«{nombre}» estará disponible próximamente.",
        )
