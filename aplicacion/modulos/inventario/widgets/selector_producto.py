from __future__ import annotations



from PySide6.QtCore import Signal

from PySide6.QtWidgets import (

    QHBoxLayout,

    QLineEdit,

    QPushButton,

    QWidget,

)



from aplicacion.framework.lookup.lookup_result import (

    LookupResult,

)

from aplicacion.maestros.productos.producto_dialogo import (

    abrir_dialogo_nuevo_producto,

    producto_a_lookup_result,

)

from aplicacion.maestros.productos.producto_lookup_dialog import (

    ProductoLookupDialog,

)

from aplicacion.recursos.ui.botones import Botones





class SelectorProducto(QWidget):



    seleccionado = Signal(

        object,

    )



    def __init__(

        self,

        parent=None,

        *,

        permitir_limpiar: bool = True,

        permitir_crear: bool = True,

    ):



        super().__init__(

            parent,

        )



        self._resultado: LookupResult | None = (

            None

        )



        self._permitir_limpiar = (

            permitir_limpiar

        )



        self._permitir_crear = (

            permitir_crear

        )



        self._crear_ui()



    def _crear_ui(self):



        layout = QHBoxLayout(

            self,

        )



        layout.setContentsMargins(

            0,

            0,

            0,

            0,

        )



        self.txt = QLineEdit()



        self.txt.setReadOnly(

            True,

        )



        self.txt.setPlaceholderText(

            "Seleccione o cree un producto",

        )



        self.txt.setToolTip(

            "Use Buscar para elegir un producto existente "

            "o Nuevo para registrarlo sin salir del formulario.",

        )



        self.btn_buscar = Botones.buscar()



        layout.addWidget(

            self.txt,

            1,

        )



        if self._permitir_crear:



            self.btn_crear = Botones.nuevo()



            self.btn_crear.setText(

                "Nuevo",

            )



            self.btn_crear.setToolTip(

                "Registrar un producto nuevo",

            )



            self.btn_crear.clicked.connect(

                self.crear_producto,

            )



            layout.addWidget(

                self.btn_crear,

            )



        layout.addWidget(

            self.btn_buscar,

        )



        if self._permitir_limpiar:



            self.btn_limpiar = QPushButton(

                "Limpiar",

            )



            self.btn_limpiar.clicked.connect(

                lambda: self.establecer(

                    None,

                ),

            )



            layout.addWidget(

                self.btn_limpiar,

            )



        self.btn_buscar.clicked.connect(

            self.buscar,

        )



    def buscar(self):



        dialogo = ProductoLookupDialog(

            parent=self.window(),

        )



        if dialogo.exec():



            self.establecer(

                dialogo.resultado,

            )



    def crear_producto(

        self,

        *,

        nombre_inicial: str = "",

    ):



        producto = abrir_dialogo_nuevo_producto(

            parent=self.window(),

            nombre_inicial=nombre_inicial,

        )



        if producto is None:



            return



        self.establecer(

            producto_a_lookup_result(

                producto,

            ),

        )



    def establecer(

        self,

        resultado: LookupResult | None,

    ):



        self._resultado = resultado



        if resultado is None:



            self.txt.clear()



        else:



            self.txt.setText(

                f"{resultado.codigo} - {resultado.texto}",

            )



        self.seleccionado.emit(

            resultado,

        )



    @property

    def resultado(

        self,

    ) -> LookupResult | None:



        return self._resultado



    @property

    def producto_id(

        self,

    ) -> int | None:



        if self._resultado is None:



            return None



        return self._resultado.valor



    @property

    def producto_variante_id(

        self,

    ) -> int | None:



        if self._resultado is None:



            return None



        return (

            self._resultado.producto_variante_id

        )



    def costo_sugerido(

        self,

    ) -> float:



        if self._resultado is None:



            return 0.0



        if self._resultado.producto_variante_id:



            from aplicacion.maestros.productos.servicios import (

                ServicioProducto,

            )



            try:



                item = ServicioProducto.resolver_item(

                    self._resultado.valor,

                    self._resultado.producto_variante_id,

                )



            except ValueError:



                item = {}



            variante = item.get(

                "variante",

            )



            if variante is not None:



                return float(

                    variante.costo or 0,

                )



        objeto = self._resultado.objeto



        if objeto is None:



            return 0.0



        return float(

            getattr(

                objeto,

                "costo",

                0,

            )

            or 0,

        )


