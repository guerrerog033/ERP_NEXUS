from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
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

    tipo="lookup" abre un buscador (LookupDialog) en vez de un
    combo con todas las opciones precargadas — para catálogos
    grandes (productos, terceros...) donde cargar todo de una vez
    no es práctico. Requiere ``datasource`` (una clase Lookup) y,
    para poder mostrar un texto legible al editar un registro
    existente (donde solo se tiene el id guardado, no el objeto
    completo), ``resolver_texto(valor) -> str``.
    """

    def __init__(
        self,
        nombre: str,
        etiqueta: str,
        *,
        tipo: str = "texto",
        opciones: list[tuple] | None = None,
        requerido: bool = False,
        datasource=None,
        resolver_texto=None,
        decimales: int = 2,
        maximo: float = 999_999_999_999.0,
    ):

        self.nombre = nombre
        self.etiqueta = etiqueta
        self.tipo = tipo
        self.opciones = opciones or []
        self.requerido = requerido
        self.datasource = datasource
        self.resolver_texto = resolver_texto

        # tipo="numero": cantidades y precios con QDoubleSpinBox. Con
        # QLineEdit, "45.000" (miles con punto, como se escribe en
        # Colombia) se guardaba como 45 y "2,5" se rechazaba.
        self.decimales = decimales

        self.maximo = maximo


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

            elif campo.tipo == "lookup":

                from aplicacion.framework.lookup.lookup_result import (
                    LookupResult,
                )
                from aplicacion.framework.lookup.lookup_widget import (
                    LookupWidget,
                )

                widget = LookupWidget(
                    campo.datasource(),
                )

                if valor is not None:

                    texto = (
                        campo.resolver_texto(valor)
                        if campo.resolver_texto
                        else str(valor)
                    )

                    widget.establecer(
                        LookupResult(
                            valor=valor,
                            texto=texto,
                        ),
                    )

            elif campo.tipo == "numero":

                widget = QDoubleSpinBox()

                widget.setDecimals(
                    campo.decimales,
                )

                widget.setRange(
                    0,
                    campo.maximo,
                )

                widget.setGroupSeparatorShown(
                    True,
                )

                widget.setButtonSymbols(
                    QDoubleSpinBox.ButtonSymbols.NoButtons,
                )

                widget.setMinimumWidth(
                    160,
                )

                if valor not in (
                    None,
                    "",
                ):

                    try:

                        widget.setValue(
                            float(
                                valor,
                            ),
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        pass

            elif campo.tipo == "fecha":

                widget = QDateEdit()

                widget.setCalendarPopup(
                    True,
                )

                widget.setDisplayFormat(
                    "yyyy-MM-dd",
                )

                widget.setMinimumDate(
                    QDate(2000, 1, 1),
                )

                widget.setSpecialValueText(
                    "(sin definir)",
                )

                if valor is not None:

                    widget.setDate(
                        QDate(
                            valor.year,
                            valor.month,
                            valor.day,
                        ),
                    )

                else:

                    widget.setDate(
                        widget.minimumDate(),
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

            if not campo.requerido:

                continue

            widget = self._widgets[
                campo.nombre
            ]

            vacio = (
                (
                    campo.tipo == "texto"
                    and not widget.text().strip()
                )
                or (
                    campo.tipo == "lookup"
                    and widget.valor() is None
                )
                or (
                    campo.tipo == "fecha"
                    and widget.date() == widget.minimumDate()
                )
                or (
                    campo.tipo == "numero"
                    and widget.value() <= 0
                )
            )

            if vacio:

                mensaje = (
                    f"El campo '{campo.etiqueta}' debe ser mayor que cero."
                    if campo.tipo == "numero"
                    else f"El campo '{campo.etiqueta}' es obligatorio."
                )

                QMessageBox.warning(
                    self,
                    "Falta información",
                    mensaje,
                )

                widget.setFocus()

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

            elif campo.tipo == "lookup":

                resultado[campo.nombre] = widget.valor()

            elif campo.tipo == "numero":

                resultado[campo.nombre] = widget.value()

            elif campo.tipo == "fecha":

                fecha_qt = widget.date()

                resultado[campo.nombre] = (
                    None
                    if fecha_qt == widget.minimumDate()
                    else fecha_qt.toPython()
                )

            else:

                resultado[campo.nombre] = (
                    widget.text().strip()
                )

        return resultado


class ListaRegistrosWidget(QWidget):
    """
    Lista editable de registros hijos de un registro padre
    (direcciones/contactos/cuentas bancarias de un tercero,
    componentes de un kit, lotes/series de un producto...). Un
    mismo widget reutilizable, configurado por instancia con las
    columnas a mostrar, los campos del formulario emergente y el
    servicio (con la interfaz listar/guardar/actualizar/eliminar)
    que lo respalda.
    """

    def __init__(
        self,
        *,
        servicio,
        columnas: list[tuple],
        campos: list[CampoRegistro],
        titulo_dialogo: str,
        campo_padre: str = "tercero_id",
        parent=None,
    ):

        super().__init__(parent)

        self.servicio = servicio

        self.columnas = columnas

        self.campos = campos

        self.titulo_dialogo = titulo_dialogo

        self.campo_padre = campo_padre

        self.padre_id = None

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

        # Doble clic sobre una fila abre la edición, como en las demás
        # tablas del ERP.
        self.tabla.doubleClicked.connect(
            lambda *_args: self._editar(),
        )

        layout.addWidget(
            self.tabla,
        )

        # Sin registro padre guardado (formulario nuevo) no hay a qué
        # asociar las filas: antes "Agregar" no hacía nada sin avisar.
        self.lbl_sin_padre = QLabel(
            "Guarde primero el registro para poder agregar elementos aquí.",
        )

        self.lbl_sin_padre.setWordWrap(
            True,
        )

        self.lbl_sin_padre.setStyleSheet(
            "color: #64748b; font-style: italic;",
        )

        layout.addWidget(
            self.lbl_sin_padre,
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

        self._actualizar_estado_padre()

    def _actualizar_estado_padre(
        self,
    ) -> None:

        hay_padre = bool(
            self.padre_id,
        )

        for boton in (
            self.btn_agregar,
            self.btn_editar,
            self.btn_eliminar,
        ):

            boton.setEnabled(
                hay_padre,
            )

        self.lbl_sin_padre.setVisible(
            not hay_padre,
        )

    def cargar(
        self,
        padre_id,
    ) -> None:

        self.padre_id = padre_id

        self._registros = (
            self.servicio.listar(
                padre_id,
            )
            if padre_id
            else []
        )

        self._refrescar_tabla()

        self._actualizar_estado_padre()

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

    def _avisar_sin_seleccion(
        self,
    ) -> None:

        if not self._registros:

            return

        QMessageBox.information(
            self,
            self.titulo_dialogo,
            "Seleccione primero una fila de la tabla.",
        )

    def _agregar(
        self,
    ) -> None:

        if not self.padre_id:

            return

        dialogo = DialogoRegistro(
            self.titulo_dialogo,
            self.campos,
            parent=self,
        )

        if dialogo.exec() != QDialog.DialogCode.Accepted:

            return

        datos = dialogo.valores()

        datos[self.campo_padre] = self.padre_id

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
            self.padre_id,
        )

    def _editar(
        self,
    ) -> None:

        registro_id = self._fila_seleccionada_id()

        if registro_id is None:

            self._avisar_sin_seleccion()

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

        datos[self.campo_padre] = self.padre_id

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
            self.padre_id,
        )

    def _eliminar(
        self,
    ) -> None:

        registro_id = self._fila_seleccionada_id()

        if registro_id is None:

            self._avisar_sin_seleccion()

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
            self.padre_id,
        )
