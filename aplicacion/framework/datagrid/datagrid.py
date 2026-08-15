from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QSizePolicy,
)

from aplicacion.framework.datagrid.toolbar import MaestroToolbar
from aplicacion.framework.ui.loading_overlay import LoadingOverlay
from aplicacion.framework.ui.table import Table


class DataGrid(QWidget):
    """
    Grid de datos reutilizable del Framework.

    Responsabilidades:

        • Toolbar unificada (CRUD + Más + búsqueda)
        • Tabla
        • Total de registros
        • Overlay de carga
    """

    def __init__(self):

        super().__init__()

        self.setObjectName(
            "DataGrid"
        )

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.setMinimumHeight(
            420
        )

        self._crear_componentes()

        self._crear_layout()

        self._crear_aliases()

    def _crear_componentes(self):

        self.toolbar = MaestroToolbar()

        self._contenedor_tabla = QWidget()

        self.tabla = Table()

        self.tabla.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        contenedor_layout = QVBoxLayout(
            self._contenedor_tabla,
        )

        contenedor_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        contenedor_layout.addWidget(
            self.tabla,
        )

        self.overlay = LoadingOverlay(
            self._contenedor_tabla,
        )

        self.lbl_total = QLabel(
            "0 registros",
        )

        self.lbl_total.setObjectName(
            "DataGridTotal",
        )

    def _crear_layout(self):

        self.layout_principal = QVBoxLayout()

        self.layout_principal.setContentsMargins(
            8,
            8,
            8,
            8,
        )

        self.layout_principal.setSpacing(
            6,
        )

        self.layout_principal.addWidget(
            self.toolbar,
            0,
        )

        self.layout_principal.addWidget(
            self._contenedor_tabla,
            1,
        )

        self.layout_principal.addWidget(
            self.lbl_total,
            0,
        )

        self.setLayout(
            self.layout_principal
        )

    def _crear_aliases(self):

        self.txt_buscar = (
            self.toolbar.txt_buscar
        )

        self.btn_nuevo = (
            self.toolbar.btn_nuevo
        )

        self.btn_editar = (
            self.toolbar.btn_editar
        )

        self.btn_consultar = (
            self.toolbar.btn_consultar
        )

        self.btn_eliminar = (
            self.toolbar.btn_eliminar
        )

        self.btn_actualizar = (
            self.toolbar.accion_actualizar
        )

        self.btn_excel = (
            self.toolbar.accion_excel
        )

        self.btn_pdf = (
            self.toolbar.accion_pdf
        )

        self.btn_imprimir = (
            self.toolbar.accion_imprimir
        )

        self.doubleClicked = (
            self.tabla.doubleClicked
        )

    def mostrar_carga(
        self,
        mensaje: str = "Cargando...",
    ) -> None:
        self.overlay.mostrar(
            mensaje,
        )

    def ocultar_carga(
        self,
    ) -> None:
        self.overlay.ocultar()

    def set_toolbar_habilitado(
        self,
        habilitado: bool,
    ) -> None:
        self.toolbar.setEnabled(
            habilitado,
        )

    def reemplazar_tabla(
        self,
        tabla,
    ):
        tabla.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        contenedor_layout = self._contenedor_tabla.layout()

        if contenedor_layout is not None:
            while contenedor_layout.count():
                item = contenedor_layout.takeAt(
                    0,
                )
                widget = item.widget()

                if widget is not None:
                    widget.setParent(
                        None,
                    )

            contenedor_layout.addWidget(
                tabla,
            )

        self.tabla = tabla

        self.doubleClicked = (
            self.tabla.doubleClicked
        )

    def __getattr__(
        self,
        nombre,
    ):

        tabla = getattr(
            self,
            "tabla",
            None,
        )

        if (
            tabla is not None
            and hasattr(
                tabla,
                nombre,
            )
        ):

            return getattr(
                tabla,
                nombre,
            )

        raise AttributeError(
            f"{type(self).__name__} no tiene el atributo '{nombre}'."
        )

    def actualizar_total(
        self,
        total: int,
    ):

        self.lbl_total.setText(
            f"{total} {'registro' if total == 1 else 'registros'}"
        )
