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

        self._crear_pie()

    # =====================================================
    # Pie: navegador de registros (estilo World Office)
    # =====================================================

    def _crear_pie(
        self,
    ) -> None:

        from PySide6.QtCore import QSize, Qt
        from PySide6.QtWidgets import QFrame, QHBoxLayout, QToolButton

        from aplicacion.framework.ui.iconos import icono_accion

        self.pie = QFrame()

        self.pie.setObjectName(
            "PieListado",
        )

        self.layout_pie = QHBoxLayout(
            self.pie,
        )

        self.layout_pie.setContentsMargins(
            4,
            2,
            4,
            2,
        )

        self.layout_pie.setSpacing(
            2,
        )

        self.botones_navegacion = {}

        for clave, icono, ayuda in (
            ("primero", "primero", "Primer registro (Inicio)"),
            ("anterior", "anterior", "Registro anterior"),
            ("siguiente", "siguiente", "Registro siguiente"),
            ("ultimo", "ultimo", "Último registro (Fin)"),
        ):

            boton = QToolButton()

            boton.setObjectName(
                "BotonNavegador",
            )

            boton.setIcon(
                icono_accion(
                    icono,
                    "#1E3A5F",
                    16,
                ),
            )

            boton.setIconSize(
                QSize(
                    16,
                    16,
                ),
            )

            boton.setToolTip(
                ayuda,
            )

            boton.setAutoRaise(
                True,
            )

            boton.setFocusPolicy(
                Qt.NoFocus,
            )

            boton.clicked.connect(
                lambda _=False, c=clave: self.navegar(
                    c,
                ),
            )

            self.botones_navegacion[
                clave
            ] = boton

            if clave == "siguiente":

                self.layout_pie.addWidget(
                    self.lbl_posicion,
                )

            self.layout_pie.addWidget(
                boton,
            )

        self.layout_pie.addSpacing(
            12,
        )

        self.layout_pie.addWidget(
            self.lbl_total,
        )

        self.layout_pie.addStretch(
            1,
        )

    @property
    def lbl_posicion(
        self,
    ):

        etiqueta = self.__dict__.get(
            "_lbl_posicion",
        )

        if etiqueta is None:

            from PySide6.QtCore import Qt

            etiqueta = QLabel(
                "Registro 0 de 0",
            )

            etiqueta.setObjectName(
                "NavegadorPosicion",
            )

            etiqueta.setAlignment(
                Qt.AlignCenter,
            )

            etiqueta.setMinimumWidth(
                130,
            )

            self.__dict__[
                "_lbl_posicion"
            ] = etiqueta

        return etiqueta

    def _filas(
        self,
    ) -> int:

        modelo = self.tabla.model() if self.tabla is not None else None

        return modelo.rowCount() if modelo is not None else 0

    def _fila_actual(
        self,
    ) -> int:

        indice = self.tabla.currentIndex()

        return indice.row() if indice.isValid() else -1

    def _filas_visibles(
        self,
    ) -> list[int]:

        return [
            fila
            for fila in range(
                self._filas(),
            )
            if not self.tabla.isRowHidden(
                fila,
            )
        ]

    def navegar(
        self,
        destino: str,
    ) -> None:

        visibles = self._filas_visibles()

        if not visibles:

            return

        actual = self._fila_actual()

        posicion = (
            visibles.index(actual)
            if actual in visibles
            else -1
        )

        if destino == "primero":

            posicion = 0

        elif destino == "ultimo":

            posicion = len(visibles) - 1

        elif destino == "anterior":

            posicion = max(
                0,
                posicion - 1,
            )

        elif destino == "siguiente":

            posicion = min(
                len(visibles) - 1,
                posicion + 1,
            )

        self.tabla.selectRow(
            visibles[posicion],
        )

        self.tabla.setFocus()

        self.actualizar_posicion()

    def actualizar_posicion(
        self,
        *_args,
    ) -> None:

        visibles = self._filas_visibles()

        actual = self._fila_actual()

        numero = (
            visibles.index(actual) + 1
            if actual in visibles
            else 0
        )

        texto = f"Registro {numero} de {len(visibles)}"

        self.lbl_posicion.setText(
            texto,
        )

        for clave, boton in self.botones_navegacion.items():

            boton.setEnabled(
                bool(visibles),
            )

        if self.isVisible():

            from aplicacion.framework.app_context import AppContext

            barra = getattr(
                AppContext,
                "barra_estado",
                None,
            )

            if barra is not None and hasattr(
                barra,
                "set_registro",
            ):

                barra.set_registro(
                    texto,
                )

    def _conectar_seleccion(
        self,
    ) -> None:

        seleccion = self.tabla.selectionModel() if self.tabla is not None else None

        if seleccion is None or seleccion is self.__dict__.get(
            "_seleccion_conectada",
        ):

            return

        seleccion.currentRowChanged.connect(
            self.actualizar_posicion,
        )

        self.__dict__[
            "_seleccion_conectada"
        ] = seleccion

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
            self.pie,
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

        if hasattr(
            tabla,
            "setAlternatingRowColors",
        ):

            tabla.setAlternatingRowColors(
                True,
            )

        self._conectar_seleccion()

        self.actualizar_posicion()

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

        self._conectar_seleccion()

        self.actualizar_posicion()

