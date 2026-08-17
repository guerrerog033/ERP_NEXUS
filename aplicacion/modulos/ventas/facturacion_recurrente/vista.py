from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
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
)

from aplicacion.framework.lookup import LookupWidget
from aplicacion.framework.ui.inquiry_page import InquiryPage
from aplicacion.maestros.terceros.cliente_lookup import ClienteLookup
from aplicacion.modulos.inventario.widgets.selector_producto import (
    SelectorProducto,
)

from .servicios import ServicioFacturaRecurrente
from .utilidades import PERIODICIDADES


class _DialogoFacturaRecurrente(QDialog):

    def __init__(
        self,
        parent=None,
        *,
        plantilla_id: int | None = None,
    ):

        super().__init__(parent)

        self.plantilla_id = plantilla_id

        self.setWindowTitle(
            "Editar plantilla recurrente"
            if plantilla_id
            else "Nueva plantilla de facturación recurrente",
        )

        self.resize(760, 540)

        self._lineas: list[dict] = []

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.nombre = QLineEdit()

        form.addRow("Nombre de la plantilla:", self.nombre)

        self.cliente = LookupWidget(ClienteLookup(), self)

        form.addRow("Cliente:", self.cliente)

        self.periodicidad = QComboBox()

        for codigo, etiqueta in PERIODICIDADES:

            self.periodicidad.addItem(etiqueta, codigo)

        indice = self.periodicidad.findData("mensual")

        if indice >= 0:

            self.periodicidad.setCurrentIndex(indice)

        form.addRow("Periodicidad:", self.periodicidad)

        self.proxima_fecha = QDateEdit()
        self.proxima_fecha.setCalendarPopup(True)
        self.proxima_fecha.setDate(QDate.currentDate())

        form.addRow(
            "Próxima fecha de generación:",
            self.proxima_fecha,
        )

        self.activa = QCheckBox("Plantilla activa")
        self.activa.setChecked(True)

        form.addRow("", self.activa)

        self.observaciones = QLineEdit()

        form.addRow("Observaciones:", self.observaciones)

        layout.addLayout(form)

        captura = QHBoxLayout()

        self.producto = SelectorProducto(self)

        self.cantidad = QDoubleSpinBox()
        self.cantidad.setMinimum(0.01)
        self.cantidad.setMaximum(999999999)
        self.cantidad.setDecimals(2)
        self.cantidad.setValue(1)

        self.precio = QDoubleSpinBox()
        self.precio.setMinimum(0)
        self.precio.setMaximum(999999999)
        self.precio.setDecimals(2)

        self.producto.seleccionado.connect(
            self._producto_seleccionado,
        )

        btn_agregar = QPushButton("Agregar línea")
        btn_agregar.clicked.connect(self._agregar_linea)

        captura.addWidget(QLabel("Producto/servicio:"))
        captura.addWidget(self.producto, 1)
        captura.addWidget(QLabel("Cant:"))
        captura.addWidget(self.cantidad)
        captura.addWidget(QLabel("Precio:"))
        captura.addWidget(self.precio)
        captura.addWidget(btn_agregar)

        layout.addLayout(captura)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(
            ["Producto/servicio", "Cantidad", "Precio", "Total"],
        )

        layout.addWidget(self.tabla)

        botones = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel,
        )

        botones.accepted.connect(self._guardar)
        botones.rejected.connect(self.reject)

        layout.addWidget(botones)

        if plantilla_id is not None:

            self._cargar(plantilla_id)

    def _producto_seleccionado(self, _resultado):

        precio = self.producto.costo_sugerido()

        if precio > 0:

            self.precio.setValue(precio)

    def _agregar_linea(self):

        descripcion = (
            self.producto.resultado.texto
            if self.producto.resultado
            else ""
        )

        if not descripcion:

            QMessageBox.warning(
                self,
                "Facturación recurrente",
                "Seleccione un producto/servicio, o escriba "
                "una descripción libre.",
            )

            return

        cantidad = self.cantidad.value()
        precio = self.precio.value()
        total = cantidad * precio

        self._lineas.append(
            {
                "producto_id": self.producto.producto_id,
                "descripcion": descripcion,
                "cantidad": cantidad,
                "precio_unitario": precio,
            },
        )

        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)

        self.tabla.setItem(
            fila, 0, QTableWidgetItem(descripcion),
        )
        self.tabla.setItem(
            fila, 1, QTableWidgetItem(f"{cantidad:,.2f}"),
        )
        self.tabla.setItem(
            fila, 2, QTableWidgetItem(f"{precio:,.2f}"),
        )
        self.tabla.setItem(
            fila, 3, QTableWidgetItem(f"{total:,.2f}"),
        )

        self.producto.establecer(None)
        self.cantidad.setValue(1)
        self.precio.setValue(0)

    def _cargar(self, plantilla_id: int):

        from aplicacion.base_datos.conexion import SessionLocal

        from .modelos import (
            FacturaRecurrente,
            FacturaRecurrenteDetalle,
        )

        db = SessionLocal()

        try:

            plantilla = (
                db.query(FacturaRecurrente)
                .filter(FacturaRecurrente.id == plantilla_id)
                .first()
            )

            if plantilla is None:

                return

            self.nombre.setText(plantilla.nombre)

            indice = self.periodicidad.findData(
                plantilla.periodicidad,
            )

            if indice >= 0:

                self.periodicidad.setCurrentIndex(indice)

            self.proxima_fecha.setDate(
                QDate(
                    plantilla.proxima_fecha.year,
                    plantilla.proxima_fecha.month,
                    plantilla.proxima_fecha.day,
                ),
            )

            self.activa.setChecked(plantilla.activa)
            self.observaciones.setText(
                plantilla.observaciones or "",
            )

            from aplicacion.framework.lookup.lookup_result import (
                LookupResult,
            )
            from aplicacion.maestros.terceros.servicio import (
                TerceroServicio,
            )

            cliente = TerceroServicio.obtener_por_id(
                plantilla.cliente_id,
            )

            if cliente is not None:

                self.cliente.establecer(
                    LookupResult(
                        valor=cliente.id,
                        texto=cliente.nombre_completo,
                    ),
                )

            detalles = (
                db.query(FacturaRecurrenteDetalle)
                .filter(
                    FacturaRecurrenteDetalle.plantilla_id
                    == plantilla_id,
                )
                .order_by(FacturaRecurrenteDetalle.orden)
                .all()
            )

            for detalle in detalles:

                cantidad = float(detalle.cantidad or 1)
                precio = float(detalle.precio_unitario or 0)
                total = cantidad * precio

                self._lineas.append(
                    {
                        "producto_id": detalle.producto_id,
                        "descripcion": detalle.descripcion,
                        "cantidad": cantidad,
                        "precio_unitario": precio,
                    },
                )

                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)

                self.tabla.setItem(
                    fila,
                    0,
                    QTableWidgetItem(detalle.descripcion),
                )
                self.tabla.setItem(
                    fila,
                    1,
                    QTableWidgetItem(f"{cantidad:,.2f}"),
                )
                self.tabla.setItem(
                    fila,
                    2,
                    QTableWidgetItem(f"{precio:,.2f}"),
                )
                self.tabla.setItem(
                    fila,
                    3,
                    QTableWidgetItem(f"{total:,.2f}"),
                )

        finally:

            db.close()

    def _guardar(self):

        cliente_id = self.cliente.valor()

        if cliente_id is None:

            QMessageBox.warning(
                self,
                "Facturación recurrente",
                "Seleccione un cliente.",
            )

            return

        try:

            ServicioFacturaRecurrente.guardar(
                {
                    "nombre": self.nombre.text(),
                    "cliente_id": cliente_id,
                    "periodicidad": (
                        self.periodicidad.currentData()
                    ),
                    "proxima_fecha": (
                        self.proxima_fecha.date().toPython()
                    ),
                    "observaciones": (
                        self.observaciones.text()
                    ),
                    "activa": self.activa.isChecked(),
                },
                self._lineas,
                id_registro=self.plantilla_id,
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Facturación recurrente",
                str(error),
            )

            return

        self.accept()


class FacturasRecurrentesPage(InquiryPage):

    titulo = "Facturación recurrente"

    _NOMBRE_EXPORT = "facturacion_recurrente"
    _TITULO_BOTON = "Actualizar"

    _COLUMNAS = [
        "Nombre",
        "Cliente",
        "Periodicidad",
        "Próxima fecha",
        "Generadas",
        "Activa",
    ]

    _ETIQUETAS_PERIODICIDAD = dict(PERIODICIDADES)

    def _crear_filtros(self) -> None:

        btn_nueva = QPushButton("Nueva plantilla")
        btn_nueva.clicked.connect(self._nueva)

        btn_editar = QPushButton("Editar")
        btn_editar.clicked.connect(self._editar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self._eliminar)

        btn_generar_una = QPushButton("Generar ahora")
        btn_generar_una.clicked.connect(
            self._generar_seleccionada,
        )

        btn_generar_pendientes = QPushButton(
            "Generar facturas pendientes",
        )
        btn_generar_pendientes.clicked.connect(
            self._generar_pendientes,
        )

        self._filas: list[dict] = []

        for boton in (
            btn_nueva,
            btn_editar,
            btn_eliminar,
            btn_generar_una,
            btn_generar_pendientes,
        ):

            self._layout_filtros.addWidget(boton)

    def _fila_seleccionada(self) -> dict | None:

        fila = self.tabla.currentRow()

        if fila < 0 or fila >= len(self._filas):

            QMessageBox.information(
                self,
                "Facturación recurrente",
                "Seleccione una plantilla en la tabla.",
            )

            return None

        return self._filas[fila]

    def _nueva(self) -> None:

        dialogo = _DialogoFacturaRecurrente(self)

        if dialogo.exec():

            self._consultar()

    def _editar(self) -> None:

        fila = self._fila_seleccionada()

        if fila is None:

            return

        dialogo = _DialogoFacturaRecurrente(
            self,
            plantilla_id=fila["id"],
        )

        if dialogo.exec():

            self._consultar()

    def _eliminar(self) -> None:

        fila = self._fila_seleccionada()

        if fila is None:

            return

        respuesta = QMessageBox.question(
            self,
            "Facturación recurrente",
            f"¿Eliminar la plantilla «{fila['nombre']}»?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if respuesta != QMessageBox.Yes:

            return

        ServicioFacturaRecurrente.eliminar(fila["id"])

        self._consultar()

    def _generar_seleccionada(self) -> None:

        fila = self._fila_seleccionada()

        if fila is None:

            return

        try:

            factura = ServicioFacturaRecurrente.generar_una(
                fila["id"],
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Facturación recurrente",
                str(error),
            )

            return

        QMessageBox.information(
            self,
            "Facturación recurrente",
            f"Se generó la factura {factura.numero}.",
        )

        self._consultar()

    def _generar_pendientes(self) -> None:

        resultado = ServicioFacturaRecurrente.generar_pendientes()

        mensaje = (
            f"Facturas generadas: {resultado['generadas']}\n"
            f"Con error: {len(resultado['errores'])}"
        )

        if resultado["errores"]:

            detalle = "\n".join(
                f"Plantilla #{pid}: {error}"
                for pid, error in resultado["errores"]
            )

            mensaje = f"{mensaje}\n\n{detalle}"

        QMessageBox.information(
            self,
            "Facturación recurrente",
            mensaje,
        )

        self._consultar()

    def _consultar(self) -> None:

        filas = ServicioFacturaRecurrente.listar()

        self._filas = filas

        self.tabla.setRowCount(len(filas))

        for indice, fila in enumerate(filas):

            valores = [
                fila["nombre"],
                fila["cliente"],
                self._ETIQUETAS_PERIODICIDAD.get(
                    fila["periodicidad"],
                    fila["periodicidad"],
                ),
                str(fila["proxima_fecha"]),
                str(fila["facturas_generadas"]),
                "Sí" if fila["activa"] else "No",
            ]

            for columna, valor in enumerate(valores):

                self.tabla.setItem(
                    indice,
                    columna,
                    QTableWidgetItem(valor),
                )

        self.tabla.resizeColumnsToContents()
