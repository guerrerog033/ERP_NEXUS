from PySide6.QtCore import (

    Signal,

    Qt,

)

from PySide6.QtWidgets import (

    QWidget,

    QVBoxLayout,

    QScrollArea,

    QFrame,

    QLabel,

    QPushButton,

)



from aplicacion.framework.menu_manifest import (

    MODULO_PENDIENTE,

    buscar_modulo as buscar_modulo_manifest,

    entradas_menu,

    grupos_visibles,

    modulo_accesible,

)

from aplicacion.interfaz.boton_modulo import (

    BotonModulo,

    BotonSubmodulo,

)

from aplicacion.recursos.estilos.tema import habilitar_fondo_qss





class BarraLateral(QWidget):



    modulo_seleccionado = Signal(

        str,

    )

    colapso_cambiado = Signal(

        bool,

    )



    ANCHO = 240

    ANCHO_COLAPSADO = 68



    @classmethod

    def entradas(cls) -> list[dict]:



        return entradas_menu()



    @classmethod

    def buscar_modulo(

        cls,

        texto: str,

    ) -> str | None:



        return buscar_modulo_manifest(

            texto,

        )



    def __init__(

        self,

    ):



        super().__init__()



        self.setObjectName(

            "BarraLateral",

        )



        habilitar_fondo_qss(

            self,

        )



        self._botones: list[BotonModulo] = []



        self._submenus: list[QWidget] = []



        self._submenu_abierto: QWidget | None = None



        self._boton_submenu_abierto: BotonModulo | None = None



        self._colapsada = False

        self._etiquetas_grupo: list[QLabel] = []

        self._etiquetas_acceso: list[QLabel] = []



        self.setFixedWidth(

            self.ANCHO,

        )



        principal = QVBoxLayout(

            self,

        )



        principal.setContentsMargins(

            0,

            0,

            0,

            0,

        )



        principal.setSpacing(

            0,

        )



        scroll = QScrollArea()



        scroll.setObjectName(

            "BarraLateralScroll",

        )



        habilitar_fondo_qss(

            scroll,

        )



        scroll.setWidgetResizable(

            True,

        )



        scroll.setFrameShape(

            QFrame.NoFrame,

        )



        scroll.setHorizontalScrollBarPolicy(

            Qt.ScrollBarAlwaysOff,

        )



        contenedor = QWidget()



        contenedor.setObjectName(

            "BarraLateralContenedor",

        )



        habilitar_fondo_qss(

            contenedor,

        )



        botones_layout = QVBoxLayout(

            contenedor,

        )



        botones_layout.setContentsMargins(

            0,

            6,

            0,

            8,

        )



        botones_layout.setSpacing(

            2,

        )



        self._contenedor_accesos = QWidget()



        self._contenedor_accesos.setObjectName(

            "BarraLateralAccesos",

        )



        habilitar_fondo_qss(

            self._contenedor_accesos,

        )



        self._layout_accesos = QVBoxLayout(

            self._contenedor_accesos,

        )



        self._layout_accesos.setContentsMargins(

            0,

            0,

            0,

            0,

        )



        self._layout_accesos.setSpacing(

            0,

        )



        botones_layout.addWidget(

            self._contenedor_accesos,

        )



        for titulo_grupo, entradas in grupos_visibles():



            etiqueta = QLabel(

                titulo_grupo.upper(),

            )



            etiqueta.setObjectName(

                "BarraLateralEtiqueta",

            )



            self._etiquetas_grupo.append(

                etiqueta,

            )



            botones_layout.addWidget(

                etiqueta,

            )



            for entrada in entradas:



                self._agregar_entrada(

                    botones_layout,

                    entrada,

                )



        botones_layout.addStretch()



        scroll.setWidget(

            contenedor,

        )



        principal.addWidget(

            scroll,

            1,

        )



        self._btn_colapsar = QPushButton(

            "«",

        )



        self._btn_colapsar.setObjectName(

            "BarraLateralToggle",

        )



        self._btn_colapsar.setCursor(

            Qt.PointingHandCursor,

        )



        self._btn_colapsar.clicked.connect(

            self.alternar_colapso,

        )



        principal.addWidget(

            self._btn_colapsar,

        )



    @property

    def esta_colapsada(

        self,

    ) -> bool:



        return self._colapsada



    def alternar_colapso(

        self,

    ) -> None:



        self._aplicar_colapso(

            not self._colapsada,

        )



    def _aplicar_colapso(

        self,

        colapsada: bool,

    ) -> None:



        self._colapsada = colapsada



        ancho = (

            self.ANCHO_COLAPSADO

            if colapsada

            else self.ANCHO

        )



        self.setFixedWidth(

            ancho,

        )



        self.setProperty(

            "colapsada",

            colapsada,

        )



        self.style().unpolish(

            self,

        )



        self.style().polish(

            self,

        )



        for etiqueta in self._etiquetas_grupo:



            etiqueta.setVisible(

                not colapsada,

            )



        for etiqueta in self._etiquetas_acceso:



            etiqueta.setVisible(

                not colapsada,

            )



        self._contenedor_accesos.setVisible(

            not colapsada,

        )



        for panel in self._submenus:



            panel.setVisible(

                False,

            )



        if colapsada:



            self._cerrar_submenus()



        for boton in self._botones:



            boton.set_expandido(

                not colapsada,

            )



            boton.configurar_ancho_colapsado(

                ancho,

            )



        self._btn_colapsar.setText(

            "»"

            if colapsada

            else "«",

        )



        self.colapso_cambiado.emit(

            colapsada,

        )



    def actualizar_accesos_rapidos(

        self,

    ) -> None:



        from aplicacion.framework.app_context import AppContext



        while self._layout_accesos.count():



            item = self._layout_accesos.takeAt(

                0,

            )



            widget = item.widget()



            if widget is not None:



                widget.deleteLater()



        navegacion = getattr(

            AppContext,

            "navegacion",

            None,

        )



        if navegacion is None:



            self._contenedor_accesos.setVisible(

                False,

            )



            return



        favoritos = [
            modulo_id
            for modulo_id in navegacion.favoritos()
            if modulo_accesible(
                modulo_id,
            )
        ]



        recientes = [

            modulo_id

            for modulo_id in navegacion.recientes()

            if modulo_id

            not in favoritos

            and modulo_accesible(
                modulo_id,
            )

        ]



        if not favoritos and not recientes:



            self._contenedor_accesos.setVisible(

                False,

            )



            return



        self._contenedor_accesos.setVisible(

            True,

        )



        if favoritos:



            self._agregar_etiqueta_acceso(

                "Favoritos",

            )



            for modulo_id in favoritos:



                self._agregar_boton_acceso(

                    navegacion.etiqueta(

                        modulo_id,

                    ),

                    modulo_id,

                )



        if recientes:



            self._agregar_etiqueta_acceso(

                "Recientes",

            )



            for modulo_id in recientes:



                self._agregar_boton_acceso(

                    navegacion.etiqueta(

                        modulo_id,

                    ),

                    modulo_id,

                )



        separador = QFrame()



        separador.setObjectName(

            "BarraLateralSeparador",

        )



        separador.setFrameShape(

            QFrame.HLine,

        )



        self._layout_accesos.addWidget(

            separador,

        )



    def _agregar_etiqueta_acceso(

        self,

        titulo: str,

    ) -> None:



        etiqueta = QLabel(

            titulo.upper(),

        )



        etiqueta.setObjectName(

            "BarraLateralEtiquetaAcceso",

        )



        self._etiquetas_acceso.append(

            etiqueta,

        )



        self._layout_accesos.addWidget(

            etiqueta,

        )



    def _agregar_boton_acceso(

        self,

        titulo: str,

        modulo_id: str,

    ) -> None:



        boton = BotonSubmodulo(

            titulo,

            modulo_id,

            margen_izquierdo=28,

        )



        boton.clicked.connect(



            lambda _checked=False,

            nombre=modulo_id: self._seleccionar(

                nombre,

            ),



        )



        boton.favorito_solicitado.connect(

            self._on_favorito_solicitado,

        )



        self._layout_accesos.addWidget(

            boton,

        )



    def _on_favorito_solicitado(

        self,

        _modulo_id: str,

    ) -> None:



        self.actualizar_accesos_rapidos()



    def _agregar_entrada(

        self,

        botones_layout: QVBoxLayout,

        entrada: dict,

    ) -> None:



        pendiente = bool(

            entrada.get(

                "pendiente",

            ),

        )



        modulo = entrada.get(

            "modulo",

            MODULO_PENDIENTE

            if pendiente

            else "",

        )



        boton = BotonModulo(



            entrada["icono"],



            entrada["titulo"],



            modulo,



            pendiente=pendiente,



        )



        submenu = entrada.get(

            "submenu",

        )



        if submenu and len(submenu) == 1:



            boton.clicked.connect(



                lambda _checked=False,

                nombre=submenu[0][1]: self._seleccionar(

                    nombre,

                ),



            )



            self._botones.append(

                boton,

            )



            botones_layout.addWidget(

                boton,

            )



            return



        if submenu:



            grupo = QWidget()



            grupo_layout = QVBoxLayout(

                grupo,

            )



            grupo_layout.setContentsMargins(

                0,

                0,

                0,

                0,

            )



            grupo_layout.setSpacing(

                0,

            )



            grupo_layout.addWidget(

                boton,

            )



            sub_contenedor = QWidget()



            sub_contenedor.setObjectName(

                "BarraLateralSubmenu",

            )



            sub_contenedor.setVisible(

                False,

            )



            habilitar_fondo_qss(

                sub_contenedor,

            )



            sub_layout = QVBoxLayout(

                sub_contenedor,

            )



            sub_layout.setContentsMargins(

                0,

                0,

                0,

                0,

            )



            sub_layout.setSpacing(

                0,

            )



            for titulo, modulo_sub in submenu:



                sub_boton = BotonSubmodulo(

                    titulo,

                    modulo_sub,

                )



                sub_boton.clicked.connect(



                    lambda _checked=False,

                    nombre=modulo_sub: self._seleccionar(

                        nombre,

                    ),



                )



                sub_boton.favorito_solicitado.connect(

                    self._on_favorito_solicitado,

                )



                sub_layout.addWidget(

                    sub_boton,

                )



            grupo_layout.addWidget(

                sub_contenedor,

            )



            self._submenus.append(

                sub_contenedor,

            )



            boton.clicked.connect(



                lambda _checked=False,

                btn=boton,

                panel=sub_contenedor: self._alternar_submenu(

                    btn,

                    panel,

                ),



            )



            self._botones.append(

                boton,

            )



            botones_layout.addWidget(

                grupo,

            )



            return



        if pendiente:



            self._botones.append(

                boton,

            )



            botones_layout.addWidget(

                boton,

            )



            return



        boton.clicked.connect(



            lambda _checked=False,

            nombre=modulo: self._seleccionar(

                nombre,

            ),



        )



        self._botones.append(

            boton,

        )



        botones_layout.addWidget(

            boton,

        )



    def _alternar_submenu(

        self,

        boton: BotonModulo,

        panel: QWidget,

    ) -> None:



        abierto = (

            panel.isVisible()

            and self._submenu_abierto is panel

        )



        self._cerrar_submenus()



        if abierto:



            return



        panel.setVisible(

            True,

        )



        self._submenu_abierto = panel



        self._boton_submenu_abierto = boton



        boton.set_submenu_abierto(

            True,

        )



    def _cerrar_submenus(

        self,

    ) -> None:



        for panel in self._submenus:



            panel.setVisible(

                False,

            )



        for boton in self._botones:



            boton.set_submenu_abierto(

                False,

            )



        self._submenu_abierto = None



        self._boton_submenu_abierto = None



    def _seleccionar(

        self,

        modulo: str,

    ) -> None:



        self.modulo_seleccionado.emit(

            modulo,

        )


