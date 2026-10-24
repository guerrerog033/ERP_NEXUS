from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)
from aplicacion.framework.form import FormEngine
from aplicacion.framework.ui.lista_registros_widget import (
    CampoRegistro,
    ListaRegistrosWidget,
)

from aplicacion.maestros.productos.datasource import (
    ProductoDataSource,
)
from aplicacion.maestros.productos.kit_servicio import (
    ServicioProductoKit,
)
from aplicacion.maestros.productos.producto_lookup import (
    ProductoLookup,
)
from aplicacion.modulos.inventario.lote_serie_servicio import (
    ServicioLoteSerie,
)

from aplicacion.maestros.productos.imagen_producto import (
    ImagenProductoWidget,
)

from aplicacion.maestros.productos.lista_precios_widget import (
    ListaPreciosProductoWidget,
)
from aplicacion.maestros.productos.precio_volumen_servicio import (
    ServicioPrecioVolumenProducto,
)

from aplicacion.maestros.productos.producto_definition import (
    ProductoDefinition,
)

from aplicacion.maestros.productos.servicios import (
    ServicioProducto,
)
from aplicacion.maestros.listas_precio.servicios import (
    ServicioListaPrecio,
)
from aplicacion.maestros.impuestos.iva_catalogo import (
    id_iva_predeterminado,
)
from aplicacion.maestros.productos.atributos_variante_widget import (
    AtributosVarianteWidget,
)
from aplicacion.maestros.productos.dialogo_variantes_producto import (
    DialogoVariantesProducto,
)
from aplicacion.maestros.productos.variantes_widget import (
    VariantesProductoWidget,
)
from aplicacion.recursos.ui.botones import Botones

class FormularioProducto(FormularioBase):

    titulo = "Productos"

    definition = ProductoDefinition

    datasource = ProductoDataSource

    ancho = 1200

    alto = 860

    def _crear_grupo_contenedor(
        self,
        titulo: str,
        widget: QWidget,
    ) -> QGroupBox:

        grupo = QGroupBox(
            titulo,
        )

        grupo.setStyleSheet(
            """
            QGroupBox {
                font-size: 14px;
                font-weight: 600;
                border: 1px solid #C3CCD8;
                border-radius: 3px;
                margin-top: 8px;
                padding-top: 12px;
                background: #F2F4F7;
            }
            QGroupBox::title {
                left: 12px;
                padding: 0 6px;
            }
            """
        )

        layout = QVBoxLayout(
            grupo,
        )

        layout.setContentsMargins(
            12,
            14,
            12,
            12,
        )

        layout.addWidget(
            widget,
        )

        return grupo

    def _preparar_campos_iva(
        self,
    ):

        from aplicacion.maestros.impuestos.iva_catalogo import (
            id_iva_predeterminado,
            opciones_iva_combo,
        )
        from aplicacion.maestros.impuestos.servicios import (
            ServicioImpuesto,
        )

        ServicioImpuesto.inicializar_predeterminados()

        opciones = opciones_iva_combo()

        predeterminado = id_iva_predeterminado()

        for grupo in self.definition.grupos:

            for campo in grupo.campos:

                if campo.nombre not in (
                    "impuesto_venta_id",
                    "impuesto_compra_id",
                ):

                    continue

                campo.opciones = list(
                    opciones,
                )

                if (
                    not self.es_edicion
                    and predeterminado
                    is not None
                ):

                    campo.valor_inicial = (
                        predeterminado
                    )

    def _crear_formulario(self):

        if self.definition is None:

            return

        self._preparar_campos_iva()

        self.engine = FormEngine(
            self.definition,
        )

        # Diseño de escritorio (World Office / Sysplus):
        #   fila 1: Identificación | Imagen
        #   fila 2: Precios + utilidad | Impuestos | Inventario
        #   fila 3: pestañas (listas de precio, volumen, descripción,
        #           existencias, movimientos, kit, lotes)
        contenedor = QWidget()

        layout_raiz = QVBoxLayout(
            contenedor,
        )

        layout_raiz.setContentsMargins(
            0,
            0,
            0,
            4,
        )

        layout_raiz.setSpacing(
            8,
        )

        panel_campos = QWidget()

        panel_campos.setLayout(
            self.engine.construir(),
        )

        self.btn_gestionar_variantes = Botones.editar()

        self.btn_gestionar_variantes.setText(
            "Configurar variantes…",
        )

        self.btn_gestionar_variantes.hide()

        self.btn_gestionar_variantes.clicked.connect(
            self._abrir_dialogo_variantes,
        )

        self._insertar_boton_variantes(
            panel_campos,
        )

        grupos = {
            grupo.title(): grupo
            for grupo in panel_campos.findChildren(
                QGroupBox,
            )
        }

        # ---- Fila 1: identificación + imagen ----
        fila_superior = QHBoxLayout()

        fila_superior.setSpacing(
            10,
        )

        if "Identificación" in grupos:

            fila_superior.addWidget(
                grupos["Identificación"],
                1,
            )

        self.imagen_widget = ImagenProductoWidget()

        grupo_imagen = self._crear_grupo_contenedor(
            "Imagen",
            self.imagen_widget,
        )

        grupo_imagen.setFixedWidth(
            270,
        )

        fila_superior.addWidget(
            grupo_imagen,
        )

        layout_raiz.addLayout(
            fila_superior,
        )

        # ---- Fila 2: precios / impuestos / inventario ----
        fila_media = QHBoxLayout()

        fila_media.setSpacing(
            10,
        )

        self.lbl_utilidad = QLabel(
            "—",
        )

        self.lbl_utilidad.setObjectName(
            "CajaDocumentoSaldo",
        )

        self.lbl_utilidad.setToolTip(
            "Utilidad estimada: precio de venta sin IVA menos el costo.",
        )

        grupo_precios = grupos.get(
            "Precios",
        )

        if grupo_precios is not None and isinstance(
            grupo_precios.layout(),
            QFormLayout,
        ):

            grupo_precios.layout().addRow(
                "Utilidad estimada",
                self.lbl_utilidad,
            )

        for titulo_grupo in (
            "Precios",
            "Impuestos",
            "Inventario",
        ):

            if titulo_grupo in grupos:

                grupos[titulo_grupo].setSizePolicy(
                    QSizePolicy.Expanding,
                    QSizePolicy.Maximum,
                )

                fila_media.addWidget(
                    grupos[titulo_grupo],
                    1,
                    Qt.AlignTop,
                )

        layout_raiz.addLayout(
            fila_media,
        )

        # ---- Fila 3: pestañas ----
        self.pestanas_producto = QTabWidget()

        self.pestanas_producto.setObjectName(
            "PestanasDocumento",
        )

        self.pestanas_producto.setMinimumHeight(
            230,
        )

        self.lista_precios_widget = (
            ListaPreciosProductoWidget()
        )

        self.pestanas_producto.addTab(
            self._pagina_pestana(
                self.lista_precios_widget,
            ),
            "Listas de precio",
        )

        self.precio_volumen_widget = ListaRegistrosWidget(
            servicio=ServicioPrecioVolumenProducto,
            columnas=[
                ("cantidad_minima", "Cantidad mínima"),
                ("precio", "Precio"),
            ],
            campos=[
                CampoRegistro(
                    "cantidad_minima",
                    "Cantidad mínima",
                    tipo="numero",
                    requerido=True,
                ),
                CampoRegistro(
                    "precio",
                    "Precio",
                    tipo="numero",
                    requerido=True,
                ),
            ],
            titulo_dialogo="Escalón de precio por volumen",
            campo_padre="producto_id",
        )

        self.pestanas_producto.addTab(
            self._pagina_pestana(
                self.precio_volumen_widget,
            ),
            "Precios por volumen",
        )

        grupo_adicional = grupos.get(
            "Información adicional",
        )

        if grupo_adicional is not None:

            grupo_adicional.setTitle(
                "",
            )

            self.pestanas_producto.addTab(
                self._pagina_pestana(
                    grupo_adicional,
                ),
                "Descripción",
            )

        self.tabla_existencias = self._tabla_consulta(
            [
                "Bodega",
                "Existencia",
                "Reservada",
                "Disponible",
            ],
        )

        self.pestanas_producto.addTab(
            self._pagina_pestana(
                self.tabla_existencias,
            ),
            "Existencias",
        )

        self.tabla_movimientos = self._tabla_consulta(
            [
                "Fecha",
                "Tipo",
                "Bodega",
                "Cantidad",
                "Costo unit.",
                "Saldo",
                "Referencia",
            ],
        )

        self.pestanas_producto.addTab(
            self._pagina_pestana(
                self.tabla_movimientos,
            ),
            "Movimientos",
        )

        self._contenedor_variantes = QWidget()

        self._contenedor_variantes.hide()

        layout_oculto = QVBoxLayout(
            self._contenedor_variantes,
        )

        self.atributos_variante_widget = (
            AtributosVarianteWidget()
        )

        self.variantes_widget = (
            VariantesProductoWidget()
        )

        layout_oculto.addWidget(
            self.atributos_variante_widget,
        )

        layout_oculto.addWidget(
            self.variantes_widget,
        )

        layout_raiz.addWidget(
            self._contenedor_variantes,
        )

        self.kit_componentes_widget = ListaRegistrosWidget(
            servicio=ServicioProductoKit,
            columnas=[
                ("componente_codigo", "Código"),
                ("componente_nombre", "Producto"),
                ("cantidad", "Cantidad"),
            ],
            campos=[
                CampoRegistro(
                    "componente_id",
                    "Producto",
                    tipo="lookup",
                    datasource=ProductoLookup,
                    requerido=True,
                    resolver_texto=self._texto_producto_componente,
                ),
                CampoRegistro(
                    "cantidad",
                    "Cantidad",
                    tipo="numero",
                    decimales=4,
                    requerido=True,
                ),
            ],
            titulo_dialogo="Componente del kit",
            campo_padre="kit_id",
        )

        self._grupo_kit = self._pagina_pestana(
            self.kit_componentes_widget,
        )

        self._grupo_kit.hide()

        self._pagina_kit = self._pagina_pestana(
            self._grupo_kit,
        )

        self.pestanas_producto.addTab(
            self._pagina_kit,
            "Componentes del kit",
        )

        self.lote_serie_widget = ListaRegistrosWidget(
            servicio=ServicioLoteSerie,
            columnas=[
                ("numero", "Número"),
                ("tipo", "Tipo"),
                ("fecha_vencimiento", "Vencimiento"),
                ("notas", "Notas"),
            ],
            campos=[
                CampoRegistro(
                    "numero",
                    "Número de lote/serie",
                    requerido=True,
                ),
                CampoRegistro(
                    "fecha_fabricacion",
                    "Fecha de fabricación",
                    tipo="fecha",
                ),
                CampoRegistro(
                    "fecha_vencimiento",
                    "Fecha de vencimiento",
                    tipo="fecha",
                ),
                CampoRegistro(
                    "notas",
                    "Notas",
                ),
            ],
            titulo_dialogo="Lote / número de serie",
            campo_padre="producto_id",
        )

        self._grupo_lote_serie = self._pagina_pestana(
            self.lote_serie_widget,
        )

        self._grupo_lote_serie.hide()

        self._pagina_lote_serie = self._pagina_pestana(
            self._grupo_lote_serie,
        )

        self.pestanas_producto.addTab(
            self._pagina_lote_serie,
            "Lotes / series",
        )

        layout_raiz.addWidget(
            self.pestanas_producto,
            1,
        )

        if not self.es_edicion:

            self._precargar_listas_precio()

        self.atributos_variante_widget.cambio.connect(
            self._sincronizar_atributos_variantes,
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

        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }",
        )

        scroll.setWidget(
            contenedor,
        )

        self.card.agregar_widget(
            scroll,
        )

        self.card.contenido.setStretch(
            self.card.contenido.count() - 1,
            1,
        )

        self._conectar_utilidad()

        self._configurar_codigo_automatico()

        widget_variantes = self.widget(
            "maneja_variantes",
        )

        if widget_variantes is not None:

            widget_variantes.toggled.connect(
                self._actualizar_variantes_visible,
            )

            self._actualizar_variantes_visible(
                widget_variantes.isChecked(),
            )


        widget_es_kit = self.widget(
            "es_kit",
        )

        if widget_es_kit is not None:

            widget_es_kit.toggled.connect(
                self._actualizar_kit_visible,
            )

            self._actualizar_kit_visible(
                widget_es_kit.isChecked(),
            )

        for nombre_campo in (
            "maneja_lote",
            "maneja_serie",
        ):

            widget_flag = self.widget(
                nombre_campo,
            )

            if widget_flag is not None:

                widget_flag.toggled.connect(
                    self._actualizar_lote_serie_visible,
                )

        self._actualizar_lote_serie_visible()

        if self.es_edicion:

            self._cargar_registro()

            self._cargar_datos_adicionales()

        self._crear_botones()

    # -----------------------------------------------------
    # Piezas del diseño de escritorio
    # -----------------------------------------------------

    @staticmethod
    def _pagina_pestana(
        widget: QWidget,
    ) -> QWidget:

        pagina = QWidget()

        layout = QVBoxLayout(
            pagina,
        )

        layout.setContentsMargins(
            6,
            6,
            6,
            6,
        )

        layout.addWidget(
            widget,
        )

        return pagina

    @staticmethod
    def _tabla_consulta(
        encabezados: list[str],
    ) -> QTableWidget:

        tabla = QTableWidget(
            0,
            len(
                encabezados,
            ),
        )

        tabla.setHorizontalHeaderLabels(
            encabezados,
        )

        tabla.verticalHeader().setVisible(
            False,
        )

        tabla.setEditTriggers(
            QAbstractItemView.NoEditTriggers,
        )

        tabla.setSelectionBehavior(
            QAbstractItemView.SelectRows,
        )

        tabla.setAlternatingRowColors(
            True,
        )

        tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch,
        )

        return tabla

    def _sincronizar_pestanas(
        self,
    ) -> None:

        pestanas = getattr(
            self,
            "pestanas_producto",
            None,
        )

        if pestanas is None:

            return

        for pagina, grupo in (
            (
                getattr(self, "_pagina_kit", None),
                getattr(self, "_grupo_kit", None),
            ),
            (
                getattr(self, "_pagina_lote_serie", None),
                getattr(self, "_grupo_lote_serie", None),
            ),
        ):

            if pagina is None or grupo is None:

                continue

            indice = pestanas.indexOf(
                pagina,
            )

            if indice >= 0:

                pestanas.setTabVisible(
                    indice,
                    not grupo.isHidden(),
                )

    def _conectar_utilidad(
        self,
    ) -> None:

        for nombre in (
            "precio_venta",
            "costo",
        ):

            widget = self.widget(
                nombre,
            )

            if widget is not None and hasattr(
                widget,
                "valueChanged",
            ):

                widget.valueChanged.connect(
                    lambda *_a: self._actualizar_utilidad(),
                )

        incluye = self.widget(
            "precio_incluye_iva",
        )

        if incluye is not None and hasattr(
            incluye,
            "toggled",
        ):

            incluye.toggled.connect(
                lambda *_a: self._actualizar_utilidad(),
            )

        impuesto = self.widget(
            "impuesto_venta_id",
        )

        if impuesto is not None and hasattr(
            impuesto,
            "currentIndexChanged",
        ):

            impuesto.currentIndexChanged.connect(
                lambda *_a: self._actualizar_utilidad(),
            )

        self._actualizar_utilidad()

    @staticmethod
    def _numero(
        widget,
    ) -> float:

        if widget is None:

            return 0.0

        try:

            return float(
                widget.value(),
            )

        except (
            AttributeError,
            TypeError,
            ValueError,
        ):

            return 0.0

    def _tarifa_iva_venta(
        self,
    ) -> float:

        import re

        combo = self.widget(
            "impuesto_venta_id",
        )

        if combo is None or not hasattr(
            combo,
            "currentText",
        ):

            return 0.0

        coincidencia = re.search(
            r"(\d+(?:[.,]\d+)?)\s*%",
            combo.currentText(),
        )

        if coincidencia is None:

            return 0.0

        return float(
            coincidencia.group(1).replace(
                ",",
                ".",
            ),
        )

    def _actualizar_utilidad(
        self,
    ) -> None:

        etiqueta = getattr(
            self,
            "lbl_utilidad",
            None,
        )

        if etiqueta is None:

            return

        precio = self._numero(
            self.widget(
                "precio_venta",
            ),
        )

        costo = self._numero(
            self.widget(
                "costo",
            ),
        )

        incluye = self.widget(
            "precio_incluye_iva",
        )

        base = precio

        if incluye is not None and incluye.isChecked():

            tarifa = self._tarifa_iva_venta()

            base = precio / (
                1 + tarifa / 100
            ) if tarifa else precio

        if base <= 0:

            etiqueta.setText(
                "—",
            )

            etiqueta.setProperty(
                "vencido",
                False,
            )

        else:

            utilidad = base - costo

            porcentaje = utilidad / base * 100

            from aplicacion.framework.ui.documento_escritorio import (
                formato_moneda,
            )

            etiqueta.setText(
                f"{formato_moneda(utilidad)}  ({porcentaje:.1f} %)",
            )

            etiqueta.setProperty(
                "vencido",
                utilidad < 0,
            )

        etiqueta.style().unpolish(
            etiqueta,
        )

        etiqueta.style().polish(
            etiqueta,
        )

    def _cargar_existencias_y_movimientos(
        self,
    ) -> None:

        if not self.id_registro:

            return

        try:

            from aplicacion.base_datos.conexion import SessionLocal
            from aplicacion.modulos.inventario.modelos import (
                Bodega,
                ExistenciaBodega,
            )

            db = SessionLocal()

            try:

                filas = (
                    db.query(
                        ExistenciaBodega,
                        Bodega,
                    )
                    .join(
                        Bodega,
                        Bodega.id == ExistenciaBodega.bodega_id,
                    )
                    .filter(
                        ExistenciaBodega.producto_id
                        == self.id_registro,
                    )
                    .all()
                )

                existencias = [
                    (
                        f"{bodega.codigo} - {bodega.nombre}",
                        float(existencia.cantidad or 0),
                        float(existencia.cantidad_reservada or 0),
                    )
                    for existencia, bodega in filas
                ]

            finally:

                db.close()

        except Exception:

            existencias = []

        self.tabla_existencias.setRowCount(
            len(
                existencias,
            ),
        )

        for fila, (bodega, cantidad, reservada) in enumerate(
            existencias,
        ):

            for columna, texto in enumerate(
                (
                    bodega,
                    f"{cantidad:,.2f}",
                    f"{reservada:,.2f}",
                    f"{cantidad - reservada:,.2f}",
                ),
            ):

                item = QTableWidgetItem(
                    texto,
                )

                if columna:

                    item.setTextAlignment(
                        Qt.AlignRight
                        | Qt.AlignVCenter,
                    )

                self.tabla_existencias.setItem(
                    fila,
                    columna,
                    item,
                )

        try:

            from aplicacion.modulos.inventario.servicios import (
                ServicioInventario,
            )

            movimientos = ServicioInventario.consultar_kardex(
                producto_id=self.id_registro,
            )[-200:]

        except Exception:

            movimientos = []

        movimientos = list(
            reversed(
                movimientos,
            ),
        )

        self.tabla_movimientos.setRowCount(
            len(
                movimientos,
            ),
        )

        for fila, movimiento in enumerate(
            movimientos,
        ):

            fecha = movimiento.get(
                "fecha",
            )

            textos = (
                fecha.strftime("%d/%m/%Y")
                if hasattr(fecha, "strftime")
                else str(fecha or ""),
                str(movimiento.get("tipo", "")),
                str(movimiento.get("bodega", "")),
                f"{float(movimiento.get('cantidad') or 0):,.2f}",
                f"{float(movimiento.get('costo_unitario') or 0):,.2f}",
                f"{float(movimiento.get('saldo') or 0):,.2f}",
                str(movimiento.get("referencia", "")),
            )

            for columna, texto in enumerate(
                textos,
            ):

                item = QTableWidgetItem(
                    texto,
                )

                if 3 <= columna <= 5:

                    item.setTextAlignment(
                        Qt.AlignRight
                        | Qt.AlignVCenter,
                    )

                self.tabla_movimientos.setItem(
                    fila,
                    columna,
                    item,
                )

    def teclas_contexto(
        self,
    ) -> list:

        teclas = super().teclas_contexto()

        extra = [
            ("F6", "Listas de precio", lambda: self.pestanas_producto.setCurrentIndex(0)),
            ("F7", "Código de barras", self._enfocar_codigo_barras),
            ("F8", "Existencias", self._ver_existencias),
        ]

        return teclas[:1] + extra + teclas[1:]

    def _enfocar_codigo_barras(
        self,
    ) -> None:

        widget = self.widget(
            "codigo_barras",
        )

        if widget is not None:

            widget.setFocus()

            if hasattr(
                widget,
                "selectAll",
            ):

                widget.selectAll()

    def _ver_existencias(
        self,
    ) -> None:

        indice = self.pestanas_producto.indexOf(
            self.tabla_existencias.parentWidget(),
        )

        if indice >= 0:

            self.pestanas_producto.setCurrentIndex(
                indice,
            )

    def _insertar_boton_variantes(
        self,
        panel_campos: QWidget,
    ) -> None:

        checkbox = self.widget(
            "maneja_variantes",
        )

        if checkbox is None:

            return

        contenedor = checkbox.parentWidget()

        while (
            contenedor is not None
            and not isinstance(
                contenedor.layout(),
                QFormLayout,
            )
        ):

            contenedor = contenedor.parentWidget()

        if contenedor is None:

            return

        layout = contenedor.layout()

        if not isinstance(
            layout,
            QFormLayout,
        ):

            return

        layout.addRow(
            "",
            self.btn_gestionar_variantes,
        )

    def _precargar_listas_precio(
        self,
    ) -> None:

        ServicioListaPrecio.inicializar_predeterminados()

        lista = ServicioListaPrecio.obtener_predeterminada()

        if lista is None:

            return

        self.lista_precios_widget.agregar_fila(
            lista_precio_id=lista.id,
            descripcion=(
                f"{lista.codigo} - {lista.nombre}"
            ),
            precio=0.0,
            impuesto_id=id_iva_predeterminado(),
        )

    def _actualizar_variantes_visible(
        self,
        visible: bool,
    ):

        self.btn_gestionar_variantes.setVisible(
            visible,
        )

    def _actualizar_kit_visible(
        self,
        visible: bool,
    ) -> None:

        # En un producto nuevo el grupo también se muestra: la lista
        # indica que hay que guardar primero para agregar componentes
        # (antes no aparecía nada y no quedaba claro qué hacer).
        self._grupo_kit.setVisible(
            visible,
        )

        self._sincronizar_pestanas()

    def _actualizar_lote_serie_visible(
        self,
        _valor=None,
    ) -> None:

        widget_lote = self.widget(
            "maneja_lote",
        )

        widget_serie = self.widget(
            "maneja_serie",
        )

        requiere = bool(
            (
                widget_lote is not None
                and widget_lote.isChecked()
            )
            or (
                widget_serie is not None
                and widget_serie.isChecked()
            )
        )

        self._grupo_lote_serie.setVisible(
            requiere,
        )

        self._sincronizar_pestanas()

    @staticmethod
    def _texto_producto_componente(
        valor,
    ) -> str:

        producto = ServicioProducto.obtener_por_id(
            valor,
        )

        if producto is None:

            return str(valor)

        return f"{producto.codigo} - {producto.nombre}"

    def _abrir_dialogo_variantes(
        self,
    ) -> None:

        dialogo = DialogoVariantesProducto(
            definiciones=(
                self.atributos_variante_widget.obtener_definiciones()
            ),
            filas=(
                self.variantes_widget.obtener_filas()
            ),
            parent=self,
        )

        if dialogo.exec():

            self.atributos_variante_widget.cargar(
                [
                    item["nombre"]
                    for item in dialogo.obtener_definiciones()
                ],
            )

            self.variantes_widget.establecer_atributos(
                dialogo.obtener_definiciones(),
            )

            self.variantes_widget.cargar_filas(
                dialogo.obtener_filas(),
            )

    def _sincronizar_atributos_variantes(
        self,
    ):

        self.variantes_widget.establecer_atributos(
            self.atributos_variante_widget.obtener_definiciones(),
        )

    def _configurar_codigo_automatico(self):

        if (
            self.es_edicion
            or not ServicioProducto.codigo_automatico_habilitado()
        ):

            return

        widget_codigo = self.widget(
            "codigo",
        )

        if widget_codigo is None:

            return

        widget_codigo.setText(
            ServicioProducto.generar_codigo(),
        )

        widget_codigo.setReadOnly(
            True,
        )

    def _cargar_datos_adicionales(self):

        registro = self.datasource.obtener_completo(
            self.id_registro,
        )

        if registro is None:

            return

        if registro.imagen:

            self.imagen_widget.establecer_ruta_relativa(
                registro.imagen,
            )

        filas = ServicioProducto.obtener_precios_formulario(
            registro,
        )

        self.lista_precios_widget.cargar_filas(
            filas,
        )

        filas_variantes, definiciones = (
            ServicioProducto.obtener_variantes_formulario(
                registro,
            )
        )

        self.atributos_variante_widget.cargar(
            [
                item["nombre"]
                for item in definiciones
            ],
        )

        self.variantes_widget.establecer_atributos(
            definiciones,
        )

        self.variantes_widget.cargar_filas(
            filas_variantes,
        )

        widget_variantes = self.widget(
            "maneja_variantes",
        )

        if widget_variantes is not None:

            self._actualizar_variantes_visible(
                widget_variantes.isChecked(),
            )

        self.kit_componentes_widget.cargar(
            self.id_registro,
        )

        widget_es_kit = self.widget(
            "es_kit",
        )

        if widget_es_kit is not None:

            self._actualizar_kit_visible(
                widget_es_kit.isChecked(),
            )

        self.lote_serie_widget.cargar(
            self.id_registro,
        )

        self._actualizar_lote_serie_visible()

        self.precio_volumen_widget.cargar(
            self.id_registro,
        )

        self._cargar_existencias_y_movimientos()

        self._actualizar_utilidad()

    def _requiere_registros_relacionados(
        self,
    ) -> bool:

        for nombre_campo in (
            "es_kit",
            "maneja_lote",
            "maneja_serie",
        ):

            widget = self.widget(
                nombre_campo,
            )

            if (
                widget is not None
                and widget.isChecked()
            ):

                return True

        return False

    def guardar_exitoso(
        self,
        objeto=None,
        mensaje="Registro guardado correctamente.",
    ):
        """
        Un producto nuevo marcado como kit o con lote/serie no puede
        tener componentes ni lotes hasta existir en la base de datos.
        Antes el formulario se cerraba al guardar y había que volver a
        abrirlo para agregarlos; ahora queda abierto en modo edición.
        """

        registro_id = getattr(
            objeto,
            "id",
            None,
        )

        if (
            self.es_edicion
            or registro_id is None
            or not self._requiere_registros_relacionados()
        ):

            super().guardar_exitoso(
                objeto,
                mensaje,
            )

            return

        from aplicacion.framework.form.modo import (
            ModoFormulario,
        )

        self.id_registro = registro_id

        self.modo = ModoFormulario.EDICION

        self.es_edicion = True

        # Recarga desde la BD para que precios y variantes queden con
        # sus ids y un segundo "Guardar" actualice en vez de duplicar.
        self._cargar_registro()

        self._cargar_datos_adicionales()

        self.guardado.emit()

        self.mostrar_info(
            "Producto guardado. Ya puede agregar los componentes "
            "del kit o los lotes / números de serie y volver a "
            "guardar si cambia algo más."
        )

    def valores(self):

        datos = super().valores()

        archivo = self.imagen_widget.archivo_pendiente()

        if archivo:

            datos["_imagen_archivo"] = archivo

        elif self.imagen_widget.ruta_relativa():

            datos["imagen"] = (
                self.imagen_widget.ruta_relativa()
            )

        datos["_listas_precios"] = (
            self.lista_precios_widget.obtener_filas()
        )

        datos["_variantes"] = (
            self.variantes_widget.obtener_filas()
        )

        datos["_atributos_variante"] = (
            self.atributos_variante_widget.obtener_definiciones()
        )

        return datos
