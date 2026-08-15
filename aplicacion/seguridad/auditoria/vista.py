from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.base.page import Page
from aplicacion.framework.datagrid.datagrid import DataGrid
from aplicacion.seguridad.acceso import panel_seguridad_visible
from aplicacion.seguridad.auditoria.servicios import (
    ServicioAuditoria,
)


class VistaAuditoria(Page):

    titulo = "Auditoría"

    icono = "contabilidad"

    def __init__(
        self,
        parent=None,
    ):

        if not panel_seguridad_visible():

            raise PermissionError(
                "No tiene permisos para ver la auditoría.",
            )

        super().__init__(
            parent,
        )

        self._crear_contenido()
        self._cargar_datos()

    def _crear_contenido(self):

        titulo = QLabel(
            "Bitácora de auditoría",
        )

        titulo.setStyleSheet(
            "font-size:18px;font-weight:bold;padding:4px 0;",
        )

        self.agregar_widget(
            titulo,
            stretch=0,
        )

        filtros = QWidget()

        form = QFormLayout(
            filtros,
        )

        self.txt_usuario = QLineEdit()
        self.txt_accion = QLineEdit()
        self.txt_buscar = QLineEdit()

        form.addRow(
            "Usuario",
            self.txt_usuario,
        )

        form.addRow(
            "Acción",
            self.txt_accion,
        )

        form.addRow(
            "Buscar",
            self.txt_buscar,
        )

        self.agregar_widget(
            filtros,
            stretch=0,
        )

        acciones = QHBoxLayout()

        self.btn_filtrar = QPushButton(
            "Filtrar",
        )

        self.btn_filtrar.clicked.connect(
            self._cargar_datos,
        )

        self.lbl_total = QLabel()

        acciones.addWidget(
            self.btn_filtrar,
        )

        acciones.addStretch()

        acciones.addWidget(
            self.lbl_total,
        )

        contenedor_acciones = QWidget()

        contenedor_acciones.setLayout(
            acciones,
        )

        self.agregar_widget(
            contenedor_acciones,
            stretch=0,
        )

        self.grid = DataGrid()

        self.tabla = self.grid.tabla

        self.grid.toolbar.actualizar.connect(
            self._cargar_datos,
        )

        self.agregar_widget(
            self.grid,
            stretch=1,
        )

    def _cargar_datos(self):

        columnas = [
            "Fecha",
            "Usuario",
            "Acción",
            "Entidad",
            "Detalle",
            "Estado",
        ]

        self.tabla.clear()
        self.tabla.setColumnCount(
            len(columnas),
        )
        self.tabla.setHorizontalHeaderLabels(
            columnas,
        )
        self.tabla.setRowCount(
            0,
        )

        registros = ServicioAuditoria.listar(
            usuario=self.txt_usuario.text(),
            accion=self.txt_accion.text(),
            texto=self.txt_buscar.text(),
        )

        for fila, registro in enumerate(
            registros,
        ):

            self.tabla.insertRow(
                fila,
            )

            fecha = ""

            if registro.fecha is not None:

                fecha = registro.fecha.strftime(
                    "%Y-%m-%d %H:%M:%S",
                )

            entidad = registro.entidad or ""

            if (
                registro.entidad_id
                is not None
            ):

                entidad = (
                    f"{entidad}#{registro.entidad_id}"
                )

            valores = [
                fecha,
                registro.usuario or "",
                registro.accion or "",
                entidad,
                registro.detalle or "",
                "OK"
                if registro.exito
                else "ERROR",
            ]

            for columna, valor in enumerate(
                valores,
            ):

                item = QTableWidgetItem(
                    valor,
                )

                if columna == 5:

                    item.setTextAlignment(
                        Qt.AlignCenter,
                    )

                self.tabla.setItem(
                    fila,
                    columna,
                    item,
                )

        self.grid.actualizar_total(
            len(registros),
        )

        self.lbl_total.setText(
            f"Registros en BD: {ServicioAuditoria.contar()}"
        )
