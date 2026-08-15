from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from aplicacion.framework.base.formulario_base import (
    FormularioBase,
)
from aplicacion.framework.form import FormEngine

from aplicacion.maestros.productos.datasource import (
    ProductoDataSource,
)

from aplicacion.maestros.productos.imagen_producto import (
    ImagenProductoWidget,
)

from aplicacion.maestros.productos.lista_precios_widget import (
    ListaPreciosProductoWidget,
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

    ancho = 920

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
                border: 1px solid #d8dee9;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 12px;
                background: white;
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

        contenedor = QWidget()

        layout_raiz = QVBoxLayout(
            contenedor,
        )

        layout_raiz.setContentsMargins(
            4,
            4,
            4,
            8,
        )

        layout_raiz.setSpacing(
            14,
        )

        panel_campos = QWidget()

        panel_campos.setLayout(
            self.engine.construir(),
        )

        layout_raiz.addWidget(
            panel_campos,
        )

        self.btn_gestionar_variantes = Botones.editar()

        self.btn_gestionar_variantes.setText(
            "Configurar variantes (talla, color, stock)…",
        )

        self.btn_gestionar_variantes.setMinimumWidth(
            340,
        )

        self.btn_gestionar_variantes.hide()

        self.btn_gestionar_variantes.clicked.connect(
            self._abrir_dialogo_variantes,
        )

        self._insertar_boton_variantes(
            panel_campos,
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

        self.lista_precios_widget = (
            ListaPreciosProductoWidget()
        )

        layout_raiz.addWidget(
            self._crear_grupo_contenedor(
                "Listas de precio",
                self.lista_precios_widget,
            ),
        )

        if not self.es_edicion:

            self._precargar_listas_precio()

        self.atributos_variante_widget.cambio.connect(
            self._sincronizar_atributos_variantes,
        )

        self.imagen_widget = ImagenProductoWidget()

        layout_raiz.addWidget(
            self._crear_grupo_contenedor(
                "Imagen",
                self.imagen_widget,
            ),
        )

        layout_raiz.addStretch()

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

        scroll.setMinimumHeight(
            520,
        )

        scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #eef2f6;
                margin: 2px 0;
            }
            QScrollBar::handle:vertical {
                background: #90a4ae;
                border-radius: 4px;
                min-height: 28px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            """
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

        self.atributos_variante_widget.cambio.connect(
            self._sincronizar_atributos_variantes,
        )

        if self.es_edicion:

            self._cargar_registro()

            self._cargar_datos_adicionales()

        self._crear_botones()

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
