from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.base.page import Page
from aplicacion.framework.datagrid.datagrid import DataGrid
from aplicacion.framework.ui.table import Table
from aplicacion.licencias.admin.acceso import panel_admin_visible
from aplicacion.licencias.admin_servicios import (
    generar_seriales,
    listar_activaciones,
    listar_seriales,
    marcar_serial_disponible,
    obtener_resumen_sistema,
    probar_servidor_online,
    revocar_activacion,
    revocar_serial,
)
from aplicacion.licencias.ediciones import EDICIONES
from aplicacion.nucleo.configuracion import Configuracion


class MaestroAdminLicencias(Page):

    titulo = "Licencias"

    icono = "contabilidad"

    def __init__(
        self,
        parent=None,
    ):

        if not panel_admin_visible():

            raise PermissionError(
                "Panel de licencias no disponible.",
            )

        super().__init__(
            parent,
        )

        self._crear_contenido()

        self._cargar_datos()

    def _crear_contenido(
        self,
    ):

        titulo = QLabel(
            "Administración de licencias",
        )

        titulo.setStyleSheet(
            "font-size:18px;font-weight:bold;padding:4px 0;",
        )

        self.agregar_widget(
            titulo,
            stretch=0,
        )

        self.tabs = QTabWidget()

        self.tabs.addTab(
            self._crear_tab_seriales(),
            "Catálogo de seriales",
        )

        self.tabs.addTab(
            self._crear_tab_activaciones(),
            "Activaciones",
        )

        self.tabs.addTab(
            self._crear_tab_estado(),
            "Estado y servidor",
        )

        self.agregar_widget(
            self.tabs,
            stretch=1,
        )

    def _crear_tab_seriales(
        self,
    ) -> QWidget:

        contenedor = QWidget()

        layout = QVBoxLayout(
            contenedor,
        )

        formulario = QGroupBox(
            "Generar seriales",
        )

        form = QFormLayout(
            formulario,
        )

        self.cmb_edicion = QComboBox()

        for codigo, datos in EDICIONES.items():

            self.cmb_edicion.addItem(
                datos["nombre"],
                codigo,
            )

        form.addRow(
            "Edición",
            self.cmb_edicion,
        )

        self.txt_titular = QLineEdit()

        form.addRow(
            "Titular",
            self.txt_titular,
        )

        self.spin_dias = QSpinBox()

        self.spin_dias.setRange(
            0,
            3650,
        )

        self.spin_dias.setSpecialValueText(
            "Sin límite",
        )

        self.spin_dias.setValue(
            365,
        )

        form.addRow(
            "Días validez (0 = sin límite)",
            self.spin_dias,
        )

        self.spin_max_usuarios = QSpinBox()

        self.spin_max_usuarios.setRange(
            0,
            9999,
        )

        self.spin_max_usuarios.setSpecialValueText(
            "Por edición",
        )

        self.spin_max_usuarios.setValue(
            0,
        )

        form.addRow(
            "Máx. usuarios (0 = edición)",
            self.spin_max_usuarios,
        )

        self.spin_cantidad = QSpinBox()

        self.spin_cantidad.setRange(
            1,
            50,
        )

        self.spin_cantidad.setValue(
            1,
        )

        form.addRow(
            "Cantidad",
            self.spin_cantidad,
        )

        self.btn_generar = QPushButton(
            "Generar",
        )

        self.btn_generar.clicked.connect(
            self._generar_seriales,
        )

        form.addRow(
            "",
            self.btn_generar,
        )

        layout.addWidget(
            formulario,
        )

        self.grid_seriales = DataGrid()

        self.tabla_seriales = self.grid_seriales.tabla

        self.grid_seriales.toolbar.actualizar.connect(
            self._cargar_seriales,
        )

        acciones = QHBoxLayout()

        self.btn_revocar_serial = QPushButton(
            "Revocar serial",
        )

        self.btn_revocar_serial.clicked.connect(
            self._revocar_serial_seleccionado,
        )

        self.btn_disponible = QPushButton(
            "Marcar disponible",
        )

        self.btn_disponible.clicked.connect(
            self._marcar_disponible,
        )

        acciones.addWidget(
            self.btn_revocar_serial,
        )

        acciones.addWidget(
            self.btn_disponible,
        )

        acciones.addStretch()

        layout.addWidget(
            self.grid_seriales,
            stretch=1,
        )

        layout.addLayout(
            acciones,
        )

        return contenedor

    def _crear_tab_activaciones(
        self,
    ) -> QWidget:

        contenedor = QWidget()

        layout = QVBoxLayout(
            contenedor,
        )

        self.grid_activaciones = DataGrid()

        self.tabla_activaciones = (
            self.grid_activaciones.tabla
        )

        self.grid_activaciones.toolbar.actualizar.connect(
            self._cargar_activaciones,
        )

        self.btn_revocar_activacion = QPushButton(
            "Revocar activación",
        )

        self.btn_revocar_activacion.clicked.connect(
            self._revocar_activacion_seleccionada,
        )

        layout.addWidget(
            self.grid_activaciones,
            stretch=1,
        )

        layout.addWidget(
            self.btn_revocar_activacion,
        )

        return contenedor

    def _crear_tab_estado(
        self,
    ) -> QWidget:

        contenedor = QWidget()

        layout = QVBoxLayout(
            contenedor,
        )

        self.lbl_estado = QLabel()

        self.lbl_estado.setWordWrap(
            True,
        )

        self.lbl_estado.setTextInteractionFlags(
            Qt.TextSelectableByMouse,
        )

        layout.addWidget(
            self.lbl_estado,
        )

        servidor = QGroupBox(
            "Servidor de licencias en línea",
        )

        form = QFormLayout(
            servidor,
        )

        config = (
            Configuracion.obtener(
                "licencias",
                "servidor_online",
            )
            or {}
        )

        self.lbl_online_habilitado = QLabel(
            "Sí"
            if config.get(
                "habilitado",
            )
            else "No",
        )

        form.addRow(
            "Habilitado",
            self.lbl_online_habilitado,
        )

        self.lbl_url_validar = QLabel(
            str(
                config.get(
                    "url_validar",
                    "",
                )
                or "—",
            ),
        )

        self.lbl_url_validar.setWordWrap(
            True,
        )

        form.addRow(
            "URL validar",
            self.lbl_url_validar,
        )

        self.lbl_resultado_servidor = QLabel(
            "—",
        )

        self.lbl_resultado_servidor.setWordWrap(
            True,
        )

        form.addRow(
            "Última prueba",
            self.lbl_resultado_servidor,
        )

        self.btn_probar_servidor = QPushButton(
            "Probar conexión",
        )

        self.btn_probar_servidor.clicked.connect(
            self._probar_servidor,
        )

        form.addRow(
            "",
            self.btn_probar_servidor,
        )

        layout.addWidget(
            servidor,
        )

        self.btn_actualizar_estado = QPushButton(
            "Actualizar resumen",
        )

        self.btn_actualizar_estado.clicked.connect(
            self._cargar_resumen,
        )

        layout.addWidget(
            self.btn_actualizar_estado,
        )

        layout.addStretch()

        return contenedor

    def _configurar_tabla(
        self,
        tabla: Table,
        columnas: list[str],
    ):

        tabla.clear()

        tabla.setColumnCount(
            len(columnas),
        )

        tabla.setHorizontalHeaderLabels(
            columnas,
        )

        tabla.setRowCount(
            0,
        )

    def _cargar_datos(
        self,
    ):

        self._cargar_seriales()

        self._cargar_activaciones()

        self._cargar_resumen()

    def _cargar_seriales(
        self,
    ):

        self._configurar_tabla(
            self.tabla_seriales,
            [
                "Serial",
                "Edición",
                "Estado",
                "Titular",
                "Máx. usuarios",
                "Días validez",
                "Creado",
            ],
        )

        registros = listar_seriales()

        for fila, registro in enumerate(
            registros,
        ):

            self.tabla_seriales.insertRow(
                fila,
            )

            valores = [
                registro.serial,
                registro.edicion,
                registro.estado,
                registro.titular_esperado or "",
                str(
                    registro.max_usuarios,
                ),
                (
                    str(
                        registro.dias_validez,
                    )
                    if registro.dias_validez
                    is not None
                    else "—"
                ),
                (
                    registro.fecha_creacion.strftime(
                        "%Y-%m-%d %H:%M",
                    )
                    if registro.fecha_creacion
                    else ""
                ),
            ]

            for columna, valor in enumerate(
                valores,
            ):

                item = QTableWidgetItem(
                    valor,
                )

                if columna == 0:

                    item.setData(
                        Qt.UserRole,
                        registro.serial,
                    )

                self.tabla_seriales.setItem(
                    fila,
                    columna,
                    item,
                )

        self.grid_seriales.actualizar_total(
            len(registros),
        )

    def _cargar_activaciones(
        self,
    ):

        self._configurar_tabla(
            self.tabla_activaciones,
            [
                "ID",
                "Serial",
                "Edición",
                "Titular",
                "Estado",
                "Activa",
                "Vence",
                "Activación",
            ],
        )

        registros = listar_activaciones()

        for fila, registro in enumerate(
            registros,
        ):

            self.tabla_activaciones.insertRow(
                fila,
            )

            valores = [
                str(
                    registro.id,
                ),
                registro.serial,
                registro.edicion,
                registro.titular or "",
                registro.estado,
                "Sí"
                if registro.activa
                else "No",
                (
                    registro.fecha_vencimiento.strftime(
                        "%Y-%m-%d",
                    )
                    if registro.fecha_vencimiento
                    else "—"
                ),
                (
                    registro.fecha_activacion.strftime(
                        "%Y-%m-%d %H:%M",
                    )
                    if registro.fecha_activacion
                    else ""
                ),
            ]

            for columna, valor in enumerate(
                valores,
            ):

                item = QTableWidgetItem(
                    valor,
                )

                if columna == 0:

                    item.setData(
                        Qt.UserRole,
                        registro.id,
                    )

                self.tabla_activaciones.setItem(
                    fila,
                    columna,
                    item,
                )

        self.grid_activaciones.actualizar_total(
            len(registros),
        )

    def _cargar_resumen(
        self,
    ):

        resumen = obtener_resumen_sistema()

        usuarios = resumen.get(
            "usuarios",
            {},
        )

        maximo = usuarios.get(
            "maximo",
        )

        texto_usuarios = (
            f"{usuarios.get('activos', 0)} activos"
        )

        if maximo is not None:

            texto_usuarios += (
                f" / límite {maximo}"
            )

            disponibles = usuarios.get(
                "disponibles",
            )

            if disponibles is not None:

                texto_usuarios += (
                    f" ({disponibles} disponibles)"
                )

        lineas = [
            f"Licencias habilitadas: {'Sí' if resumen.get('licencias_habilitadas') else 'No'}",
            f"Licencia válida: {'Sí' if resumen.get('licencia_valida') else 'No'}",
            f"Edición: {resumen.get('edicion') or '—'}",
            f"Serial: {resumen.get('serial') or '—'}",
            f"Titular: {resumen.get('titular') or '—'}",
            f"Vencimiento: {resumen.get('fecha_vencimiento') or '—'}",
            f"Usuarios: {texto_usuarios}",
            f"Mensaje: {resumen.get('mensaje') or '—'}",
        ]

        self.lbl_estado.setText(
            "\n".join(
                lineas,
            ),
        )

    def _serial_seleccionado(
        self,
        tabla: Table,
    ) -> str | None:

        fila = tabla.currentRow()

        if fila < 0:

            return None

        item = tabla.item(
            fila,
            0,
        )

        if item is None:

            return None

        return str(
            item.data(
                Qt.UserRole,
            )
            or item.text(),
        )

    def _id_activacion_seleccionado(
        self,
    ) -> int | None:

        fila = self.tabla_activaciones.currentRow()

        if fila < 0:

            return None

        item = self.tabla_activaciones.item(
            fila,
            0,
        )

        if item is None:

            return None

        valor = item.data(
            Qt.UserRole,
        )

        if valor is None:

            return None

        return int(
            valor,
        )

    def _generar_seriales(
        self,
    ):

        edicion = self.cmb_edicion.currentData()

        dias = self.spin_dias.value()

        max_usuarios = self.spin_max_usuarios.value()

        try:

            seriales = generar_seriales(
                edicion=edicion,
                titular=self.txt_titular.text().strip(),
                dias_validez=(
                    None
                    if dias <= 0
                    else dias
                ),
                max_usuarios=(
                    None
                    if max_usuarios <= 0
                    else max_usuarios
                ),
                cantidad=self.spin_cantidad.value(),
            )

        except Exception as error:

            QMessageBox.warning(
                self,
                "Error",
                str(
                    error,
                ),
            )

            return

        texto = "\n".join(
            seriales,
        )

        QMessageBox.information(
            self,
            "Seriales generados",
            texto,
        )

        self._cargar_seriales()

        self._cargar_resumen()

    def _revocar_serial_seleccionado(
        self,
    ):

        serial = self._serial_seleccionado(
            self.tabla_seriales,
        )

        if not serial:

            QMessageBox.information(
                self,
                "Revocar",
                "Seleccione un serial.",
            )

            return

        confirmacion = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Revocar el serial {serial}?",
        )

        if (
            confirmacion
            != QMessageBox.StandardButton.Yes
        ):

            return

        try:

            revocar_serial(
                serial,
            )

        except Exception as error:

            QMessageBox.warning(
                self,
                "Error",
                str(
                    error,
                ),
            )

            return

        self._cargar_datos()

    def _marcar_disponible(
        self,
    ):

        serial = self._serial_seleccionado(
            self.tabla_seriales,
        )

        if not serial:

            QMessageBox.information(
                self,
                "Disponible",
                "Seleccione un serial.",
            )

            return

        try:

            marcar_serial_disponible(
                serial,
            )

        except Exception as error:

            QMessageBox.warning(
                self,
                "Error",
                str(
                    error,
                ),
            )

            return

        self._cargar_seriales()

    def _revocar_activacion_seleccionada(
        self,
    ):

        activacion_id = (
            self._id_activacion_seleccionado()
        )

        if activacion_id is None:

            QMessageBox.information(
                self,
                "Revocar",
                "Seleccione una activación.",
            )

            return

        confirmacion = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Revocar la activación #{activacion_id}?",
        )

        if (
            confirmacion
            != QMessageBox.StandardButton.Yes
        ):

            return

        try:

            revocar_activacion(
                activacion_id,
            )

        except Exception as error:

            QMessageBox.warning(
                self,
                "Error",
                str(
                    error,
                ),
            )

            return

        self._cargar_datos()

    def _probar_servidor(
        self,
    ):

        resultado = probar_servidor_online()

        texto = resultado.mensaje or (
            "Conexión OK"
            if resultado.valido
            else "Sin respuesta"
        )

        self.lbl_resultado_servidor.setText(
            texto,
        )

        if resultado.valido:

            QMessageBox.information(
                self,
                "Servidor",
                texto,
            )

            return

        QMessageBox.warning(
            self,
            "Servidor",
            texto,
        )
