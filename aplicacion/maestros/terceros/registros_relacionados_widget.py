from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class CampoRegistro:
    """
    Describe un campo del formulario emergente de alta/edición
    (nombre del atributo, etiqueta visible, tipo de control).
    """

    def __init__(
        self,
        nombre: str,
        etiqueta: str,
        *,
        tipo: str = "texto",
        opciones: list[tuple] | None = None,
        requerido: bool = False,
    ):

        self.nombre = nombre
        self.etiqueta = etiqueta
        self.tipo = tipo
        self.opciones = opciones or []
        self.requerido = requerido


class DialogoRegistro(QDialog):
    """
    Formulario emergente genérico de alta/edición para un
    registro hijo de tercero, construido a partir de una lista
    de :class:`CampoRegistro`.
    """

    def __init__(
        self,
        titulo: str,
        campos: list[CampoRegistro],
        valores: dict | None = None,
        parent=None,
    ):

        super().__init__(parent)

        self.setWindowTitle(titulo)

        self.campos = campos

        self._widgets: dict = {}

        valores = valores or {}

        layout = QVBoxLayout(self)

        formulario = QFormLayout()

        for campo in campos:

            valor = valores.get(campo.nombre)

            if campo.tipo == "combo":

                widget = QComboBox()

                for dato, etiqueta in campo.opciones:

                    widget.addItem(
                        etiqueta,
                        dato,
                    )

                if valor is not None:

                    indice = widget.findData(
                        valor,
                    )

                    if indice >= 0:

                        widget.setCurrentIndex(
                            indice,
                        )

            elif campo.tipo == "bool":

                widget = QCheckBox()

                widget.setChecked(
                    bool(valor),
                )

            else:

                widget = QLineEdit()

                if valor is not None:

                    widget.setText(
                        str(valor),
                    )

            self._widgets[campo.nombre] = widget

            formulario.addRow(
                campo.etiqueta,
                widget,
            )

        layout.addLayout(
            formulario,
        )

        botones = QDialogButtonBox(
            QDialogButtonBox.Ok
            | QDialogButtonBox.Cancel,
        )

        botones.accepted.connect(
            self._validar_y_aceptar,
        )

        botones.rejected.connect(
            self.reject,
        )

        layout.addWidget(
            botones,
        )

    def _validar_y_aceptar(
        self,
    ) -> None:

        for campo in self.campos:

            if (
                campo.requerido
                and campo.tipo == "texto"
                and not self._widgets[
                    campo.nombre
                ].text().strip()
            ):

                QMessageBox.warning(
                    self,
                    "Falta información",
                    f"El campo '{campo.etiqueta}' es obligatorio.",
                )

                return

        self.accept()

    def valores(
        self,
    ) -> dict:

        resultado = {}

        for campo in self.campos:

            widget = self._widgets[
                campo.nombre
            ]

            if campo.tipo == "combo":

                resultado[campo.nombre] = (
                    widget.currentData()
                )

            elif campo.tipo == "bool":

                resultado[campo.nombre] = (
                    widget.isChecked()
                )

            else:

                resultado[campo.nombre] = (
                    widget.text().strip()
                )

        return resultado


class ListaRegistrosTerceroWidget(QWidget):
    """
    Lista editable de registros hijos de un tercero (direcciones,
    contactos, cuentas bancarias). Un mismo widget reutilizable,
    configurado por instancia con las columnas a mostrar, los
    campos del formulario emergente y el servicio (con la
    interfaz listar/guardar/actualizar/eliminar) que lo respalda.
    """

    def __init__(
        self,
        *,
        servicio,
        columnas: list[tuple],
        campos: list[CampoRegistro],
        titulo_dialogo: str,
        parent=None,
    ):

        super().__init__(parent)

        self.servicio = servicio

        self.columnas = columnas

        self.campos = campos

        self.titulo_dialogo = titulo_dialogo

        self.tercero_id = None

        self._registros: list = []

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.tabla = QTableWidget(
            0,
            len(columnas),
        )

        self.tabla.setHorizontalHeaderLabels(
            [etiqueta for _, etiqueta in columnas],
        )

        self.tabla.horizontalHeader().setStretchLastSection(
            True,
        )

        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectRows,
        )

        self.tabla.setSelectionMode(
            QAbstractItemView.SingleSelection,
        )

        self.tabla.setEditTriggers(
            QAbstractItemView.NoEditTriggers,
        )

        layout.addWidget(
            self.tabla,
        )

        barra = QHBoxLayout()

        self.btn_agregar = QPushButton(
            "Agregar",
        )

        self.btn_editar = QPushButton(
            "Editar",
        )

        self.btn_eliminar = QPushButton(
            "Eliminar",
        )

        barra.addWidget(
            self.btn_agregar,
        )

        barra.addWidget(
            self.btn_editar,
        )

        barra.addWidget(
            self.btn_eliminar,
        )

        barra.addStretch()

        layout.addLayout(
            barra,
        )

        self.btn_agregar.clicked.connect(
            self._agregar,
        )

        self.btn_editar.clicked.connect(
            self._editar,
        )

        self.btn_eliminar.clicked.connect(
            self._eliminar,
        )

    def cargar(
        self,
        tercero_id,
    ) -> None:

        self.tercero_id = tercero_id

        self._registros = (
            self.servicio.listar(
                tercero_id,
            )
            if tercero_id
            else []
        )

        self._refrescar_tabla()

    def _refrescar_tabla(
        self,
    ) -> None:

        self.tabla.setRowCount(
            0,
        )

        for registro in self._registros:

            fila = self.tabla.rowCount()

            self.tabla.insertRow(
                fila,
            )

            for columna, (campo, _etiqueta) in enumerate(
                self.columnas,
            ):

                valor = getattr(
                    registro,
                    campo,
                    "",
                )

                if isinstance(
                    valor,
                    bool,
                ):

                    valor = "Sí" if valor else ""

                item = QTableWidgetItem(
                    str(valor or ""),
                )

                if columna == 0:

                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        registro.id,
                    )

                self.tabla.setItem(
                    fila,
                    columna,
                    item,
                )

    def _fila_seleccionada_id(
        self,
    ):

        filas = self.tabla.selectionModel().selectedRows()

        if not filas:

            return None

        item = self.tabla.item(
            filas[0].row(),
            0,
        )

        return item.data(
            Qt.ItemDataRole.UserRole,
        ) if item else None

    def _agregar(
        self,
    ) -> None:

        if not self.tercero_id:

            return

        dialogo = DialogoRegistro(
            self.titulo_dialogo,
            self.campos,
            parent=self,
        )

        if dialogo.exec() != QDialog.DialogCode.Accepted:

            return

        datos = dialogo.valores()

        datos["tercero_id"] = self.tercero_id

        try:

            self.servicio.guardar(
                datos,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "No se pudo guardar",
                str(error),
            )

            return

        self.cargar(
            self.tercero_id,
        )

    def _editar(
        self,
    ) -> None:

        registro_id = self._fila_seleccionada_id()

        if registro_id is None:

            return

        registro = next(
            (
                r
                for r in self._registros
                if r.id == registro_id
            ),
            None,
        )

        if registro is None:

            return

        valores = {
            campo.nombre: getattr(
                registro,
                campo.nombre,
                None,
            )
            for campo in self.campos
        }

        dialogo = DialogoRegistro(
            self.titulo_dialogo,
            self.campos,
            valores=valores,
            parent=self,
        )

        if dialogo.exec() != QDialog.DialogCode.Accepted:

            return

        datos = dialogo.valores()

        datos["tercero_id"] = self.tercero_id

        try:

            self.servicio.actualizar(
                registro_id,
                datos,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "No se pudo guardar",
                str(error),
            )

            return

        self.cargar(
            self.tercero_id,
        )

    def _eliminar(
        self,
    ) -> None:

        registro_id = self._fila_seleccionada_id()

        if registro_id is None:

            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar",
            "¿Eliminar este registro?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if (
            respuesta
            != QMessageBox.StandardButton.Yes
        ):

            return

        self.servicio.eliminar(
            registro_id,
        )

        self.cargar(
            self.tercero_id,
        )
