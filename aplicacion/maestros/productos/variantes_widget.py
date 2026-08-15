from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from aplicacion.maestros.productos.catalogo_variantes_servicio import (
    ServicioCatalogoVariantes,
)

from aplicacion.recursos.ui.botones import Botones


COL_CODIGO = 0
COL_TALLA = 1
COL_COLOR = 2
COL_CALIBRE = 3
COL_LARGO = 4
COL_PRECIO = 5
COL_COSTO = 6
COL_EXISTENCIA = 7
COL_BARRAS = 8
COL_ACTIVO = 9
COL_BORRAR = 10

COLUMNAS_FIJAS_ANTES = 5
COLUMNAS_FIJAS_DESPUES = 6


class VariantesProductoWidget(QWidget):

    def __init__(
        self,
        parent=None,
    ):

        self._atributos: list[dict] = []

        super().__init__(
            parent,
        )

        self._crear_ui()

    def _crear_ui(self):

        layout = QVBoxLayout(
            self,
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.lbl_ayuda = QLabel()

        self.lbl_ayuda.setWordWrap(
            True,
        )

        self.lbl_ayuda.setStyleSheet(
            "color: #546e7a; padding-bottom: 4px;",
        )

        layout.addWidget(
            self.lbl_ayuda,
        )

        self.tabla = QTableWidget(
            0,
            0,
        )

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch,
        )

        self.tabla.setMinimumHeight(
            180,
        )

        layout.addWidget(
            self.tabla,
        )

        acciones = QHBoxLayout()

        btn_agregar = Botones.nuevo()

        btn_agregar.setText(
            "Agregar variante",
        )

        btn_agregar.clicked.connect(
            self._agregar_fila,
        )

        acciones.addWidget(
            btn_agregar,
        )

        acciones.addStretch()

        layout.addLayout(
            acciones,
        )

        self._actualizar_encabezados()

    def _editor_catalogo(
        self,
        tipo: str,
        valor: str = "",
    ) -> QComboBox:

        combo = QComboBox()

        combo.setEditable(
            True,
        )

        combo.addItem(
            "",
        )

        for opcion in ServicioCatalogoVariantes.listar_valores(
            tipo,
        ):

            combo.addItem(
                opcion,
            )

        texto = str(
            valor or "",
        ).strip()

        if texto:

            indice = combo.findText(
                texto,
            )

            if indice >= 0:

                combo.setCurrentIndex(
                    indice,
                )

            else:

                combo.setEditText(
                    texto,
                )

        return combo

    def _editor_atributo(
        self,
        nombre_tipo: str,
        valor: str = "",
    ) -> QWidget:

        valores = ServicioCatalogoVariantes.listar_valores(
            "atributo",
            nombre_tipo=nombre_tipo,
        )

        if valores:

            return self._editor_catalogo_atributo(
                nombre_tipo,
                valor,
            )

        editor = QLineEdit()

        editor.setText(
            str(
                valor or "",
            ),
        )

        return editor

    def _editor_catalogo_atributo(
        self,
        nombre_tipo: str,
        valor: str = "",
    ) -> QComboBox:

        combo = QComboBox()

        combo.setEditable(
            True,
        )

        combo.addItem(
            "",
        )

        for opcion in ServicioCatalogoVariantes.listar_valores(
            "atributo",
            nombre_tipo=nombre_tipo,
        ):

            combo.addItem(
                opcion,
            )

        texto = str(
            valor or "",
        ).strip()

        if texto:

            indice = combo.findText(
                texto,
            )

            if indice >= 0:

                combo.setCurrentIndex(
                    indice,
                )

            else:

                combo.setEditText(
                    texto,
                )

        return combo

    def _texto_editor(
        self,
        widget: QWidget | None,
    ) -> str:

        if widget is None:

            return ""

        if isinstance(
            widget,
            QComboBox,
        ):

            return widget.currentText().strip()

        if isinstance(
            widget,
            QLineEdit,
        ):

            return widget.text().strip()

        return ""

    def _valor_numerico(
        self,
        widget: QWidget | None,
        *,
        default: float = 0.0,
    ) -> float:

        if widget is None:

            return default

        if isinstance(
            widget,
            QDoubleSpinBox,
        ):

            return float(
                widget.value(),
            )

        if isinstance(
            widget,
            QLineEdit,
        ):

            texto = widget.text().strip().replace(
                ",",
                ".",
            )

            if not texto:

                return default

            try:

                return float(
                    texto,
                )

            except ValueError:

                return default

        return default

    def _valor_opcional_positivo(
        self,
        widget: QWidget | None,
    ) -> float | None:

        valor = self._valor_numerico(
            widget,
            default=0.0,
        )

        if valor > 0:

            return valor

        return None

    def establecer_atributos(
        self,
        definiciones: list[dict] | list[str] | None,
    ):

        datos_previos = self.obtener_filas()

        if definiciones and isinstance(
            definiciones[0],
            dict,
        ):

            self._atributos = list(
                definiciones,
            )

        else:

            from aplicacion.maestros.productos.atributos_variante_widget import (
                normalizar_clave_atributo,
            )

            self._atributos = [
                {
                    "nombre": str(nombre),
                    "clave": normalizar_clave_atributo(
                        str(nombre),
                    ),
                }
                for nombre in (
                    definiciones or []
                )
                if str(nombre).strip()
            ]

        self._actualizar_encabezados(
            datos_previos,
        )

    def _actualizar_encabezados(
        self,
        filas: list[dict] | None = None,
    ):

        encabezados = [
            "Código",
            "Talla",
            "Color",
            "Calibre",
            "Largo",
        ]

        for item in self._atributos:

            encabezados.append(
                str(
                    item.get(
                        "nombre",
                        "",
                    ),
                ),
            )

        encabezados.extend(
            [
                "Precio",
                "Costo",
                "Existencia (ref.)",
                "C. barras",
                "Activo",
                "",
            ],
        )

        filas = (
            filas
            if filas is not None
            else self.obtener_filas()
        )

        self.tabla.setColumnCount(
            len(encabezados),
        )

        self.tabla.setHorizontalHeaderLabels(
            encabezados,
        )

        self.tabla.setRowCount(
            0,
        )

        for fila in filas:

            self._agregar_fila(
                fila,
            )

        texto_attrs = (
            ", ".join(
                item["nombre"]
                for item in self._atributos
            )
            if self._atributos
            else "ninguno extra"
        )

        self.lbl_ayuda.setText(
            "Defina combinaciones con talla, color, calibre, "
            f"largo y atributos ({texto_attrs}). "
            "Existencia (referencia) por variante: solo lectura; "
            "el stock real se obtiene del kardex. "
            "Precio/costo 0 hereda del producto."
        )

    def _indice_atributo(
        self,
        indice_attr: int,
    ) -> int:

        return (
            COLUMNAS_FIJAS_ANTES
            + indice_attr
        )

    def _indice_columna_fija(
        self,
        columna_fija: int,
    ) -> int:

        if columna_fija < COL_PRECIO:

            return columna_fija

        return (
            columna_fija
            + len(self._atributos)
        )

    def _widget_celda(
        self,
        fila: int,
        columna: int,
    ):

        return self.tabla.cellWidget(
            fila,
            columna,
        )

    def _agregar_fila(
        self,
        datos=None,
    ):

        fila = self.tabla.rowCount()

        self.tabla.insertRow(
            fila,
        )

        codigo = QLineEdit()

        codigo.setPlaceholderText(
            "Auto al guardar",
        )

        if datos:

            codigo.setText(
                str(
                    datos.get(
                        "codigo",
                        "",
                    )
                    or "",
                ),
            )

        self.tabla.setCellWidget(
            fila,
            COL_CODIGO,
            codigo,
        )

        for columna, campo in (
            (COL_TALLA, "talla"),
            (COL_COLOR, "color"),
            (COL_CALIBRE, "calibre"),
            (COL_LARGO, "largo"),
        ):

            valor = ""

            if datos:

                valor = str(
                    datos.get(
                        campo,
                        "",
                    )
                    or "",
                )

            editor = self._editor_catalogo(
                campo,
                valor,
            )

            self.tabla.setCellWidget(
                fila,
                columna,
                editor,
            )

        atributos = {}

        if datos:

            atributos = dict(
                datos.get(
                    "atributos",
                )
                or {},
            )

        for indice, item in enumerate(
            self._atributos,
        ):

            clave = item["clave"]

            editor = self._editor_atributo(
                str(
                    item.get(
                        "nombre",
                        "",
                    ),
                ),
                str(
                    atributos.get(
                        clave,
                        "",
                    )
                    or "",
                ),
            )

            self.tabla.setCellWidget(
                fila,
                self._indice_atributo(
                    indice,
                ),
                editor,
            )

        precio = QDoubleSpinBox()

        precio.setRange(
            0,
            999999999999,
        )
        precio.setDecimals(
            2,
        )
        precio.setSpecialValueText(
            "Heredar",
        )

        if datos and datos.get(
            "precio_venta",
        ) is not None:

            precio.setValue(
                float(
                    datos.get(
                        "precio_venta",
                        0,
                    )
                    or 0,
                ),
            )

        self.tabla.setCellWidget(
            fila,
            self._indice_columna_fija(
                COL_PRECIO,
            ),
            precio,
        )

        costo = QDoubleSpinBox()

        costo.setRange(
            0,
            999999999999,
        )
        costo.setDecimals(
            2,
        )
        costo.setSpecialValueText(
            "Heredar",
        )

        if datos and datos.get(
            "costo",
        ) is not None:

            costo.setValue(
                float(
                    datos.get(
                        "costo",
                        0,
                    )
                    or 0,
                ),
            )

        self.tabla.setCellWidget(
            fila,
            self._indice_columna_fija(
                COL_COSTO,
            ),
            costo,
        )

        existencia = QDoubleSpinBox()

        existencia.setRange(
            0,
            999999999999,
        )
        existencia.setDecimals(
            2,
        )
        existencia.setReadOnly(
            True,
        )
        existencia.setButtonSymbols(
            QDoubleSpinBox.ButtonSymbols.NoButtons,
        )
        existencia.setToolTip(
            "Referencia de stock. El inventario real "
            "se obtiene del kardex.",
        )

        existencia.setValue(
            float(
                datos.get(
                    "existencia",
                    0,
                )
                if datos
                else 0,
            ),
        )

        self.tabla.setCellWidget(
            fila,
            self._indice_columna_fija(
                COL_EXISTENCIA,
            ),
            existencia,
        )

        barras = QLineEdit()

        if datos:

            barras.setText(
                str(
                    datos.get(
                        "codigo_barras",
                        "",
                    )
                    or "",
                ),
            )

        self.tabla.setCellWidget(
            fila,
            self._indice_columna_fija(
                COL_BARRAS,
            ),
            barras,
        )

        activo = QCheckBox()

        activo.setChecked(
            bool(
                datos.get(
                    "activo",
                    True,
                )
                if datos
                else True
            ),
        )

        activo.setStyleSheet(
            "margin-left: 12px;",
        )

        contenedor_activo = QWidget()

        layout_activo = QHBoxLayout(
            contenedor_activo,
        )

        layout_activo.setContentsMargins(
            8,
            0,
            0,
            0,
        )

        layout_activo.addWidget(
            activo,
        )

        self.tabla.setCellWidget(
            fila,
            self._indice_columna_fija(
                COL_ACTIVO,
            ),
            contenedor_activo,
        )

        btn_borrar = QPushButton(
            "✕",
        )

        btn_borrar.setFixedWidth(
            28,
        )

        btn_borrar.clicked.connect(
            lambda _c=False, f=fila: self._borrar_fila(
                f,
            ),
        )

        self.tabla.setCellWidget(
            fila,
            self._indice_columna_fija(
                COL_BORRAR,
            ),
            btn_borrar,
        )

    def _borrar_fila(
        self,
        fila: int,
    ):

        if (
            fila < 0
            or fila >= self.tabla.rowCount()
        ):

            return

        self.tabla.removeRow(
            fila,
        )

    def cargar_filas(
        self,
        filas: list[dict],
    ):

        self.tabla.setRowCount(
            0,
        )

        for fila in filas:

            self._agregar_fila(
                fila,
            )

    def obtener_filas(
        self,
    ) -> list[dict]:

        filas = []

        for fila in range(
            self.tabla.rowCount(),
        ):

            codigo = self._widget_celda(
                fila,
                COL_CODIGO,
            )
            talla = self._widget_celda(
                fila,
                COL_TALLA,
            )
            color = self._widget_celda(
                fila,
                COL_COLOR,
            )
            calibre = self._widget_celda(
                fila,
                COL_CALIBRE,
            )
            largo = self._widget_celda(
                fila,
                COL_LARGO,
            )

            atributos = {}

            for indice, item in enumerate(
                self._atributos,
            ):

                editor = self._widget_celda(
                    fila,
                    self._indice_atributo(
                        indice,
                    ),
                )

                valor = ""

                if editor is not None:

                    valor = self._texto_editor(
                        editor,
                    )

                if valor:

                    atributos[
                        item["clave"]
                    ] = valor

            precio = self._widget_celda(
                fila,
                self._indice_columna_fija(
                    COL_PRECIO,
                ),
            )
            costo = self._widget_celda(
                fila,
                self._indice_columna_fija(
                    COL_COSTO,
                ),
            )
            existencia = self._widget_celda(
                fila,
                self._indice_columna_fija(
                    COL_EXISTENCIA,
                ),
            )
            barras = self._widget_celda(
                fila,
                self._indice_columna_fija(
                    COL_BARRAS,
                ),
            )
            activo_contenedor = self._widget_celda(
                fila,
                self._indice_columna_fija(
                    COL_ACTIVO,
                ),
            )

            activo = True

            if activo_contenedor is not None:

                checkbox = activo_contenedor.findChild(
                    QCheckBox,
                )

                if checkbox is not None:

                    activo = checkbox.isChecked()

            filas.append(
                {
                    "codigo": (
                        codigo.text().strip()
                        if codigo
                        else ""
                    ),
                    "talla": self._texto_editor(
                        talla,
                    ),
                    "color": self._texto_editor(
                        color,
                    ),
                    "calibre": self._texto_editor(
                        calibre,
                    ),
                    "largo": self._texto_editor(
                        largo,
                    ),
                    "atributos": atributos,
                    "precio_venta": (
                        self._valor_opcional_positivo(
                            precio,
                        )
                    ),
                    "costo": (
                        self._valor_opcional_positivo(
                            costo,
                        )
                    ),
                    "existencia": (
                        self._valor_numerico(
                            existencia,
                        )
                    ),
                    "codigo_barras": (
                        barras.text().strip()
                        if barras
                        else ""
                    ),
                    "activo": activo,
                },
            )

        return filas
