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

        # (botón de submódulo o None, botón del módulo padre, id del
        # módulo) para resaltar en el menú la pantalla abierta.
        self._enlaces: list[tuple] = []

        self._modulo_activo: str | None = None



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

            if titulo_grupo:

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
            False,
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
        """
        La barra lateral ya no muestra Favoritos ni Recientes: solo
        el menú de módulos, para que se vea ordenada. Se conserva el
        método (lo llama el dashboard) y deja el bloque oculto.
        """

        while self._layout_accesos.count():

            item = self._layout_accesos.takeAt(
                0,
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

        self._etiquetas_acceso.clear()

        self._contenedor_accesos.setVisible(
            False,
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



        submenu = entrada.get(
            "submenu",
        )

        boton = BotonModulo(
            entrada["icono"],
            entrada["titulo"],
            modulo,
            pendiente=pendiente,
            con_submenu=bool(
                submenu
                and len(submenu) > 1
            ),
        )



        if submenu and len(submenu) == 1:



            boton.clicked.connect(



                lambda _checked=False,

                nombre=submenu[0][1]: self._seleccionar(

                    nombre,

                ),



            )

            self._enlaces.append(
                (
                    None,
                    boton,
                    submenu[0][1],
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



                self._enlaces.append(
                    (
                        sub_boton,
                        boton,
                        modulo_sub,
                    ),
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

        self._enlaces.append(
            (
                None,
                boton,
                modulo,
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

        self._aplicar_resaltado()



    def marcar_activo(
        self,
        modulo: str | None,
    ) -> None:
        """
        Resalta en el menú la pantalla abierta (y su módulo padre).
        """

        self._modulo_activo = modulo

        self._aplicar_resaltado()

    def _aplicar_resaltado(
        self,
    ) -> None:

        padres_activos = set()

        for sub_boton, padre, modulo in self._enlaces:

            activo = (
                modulo == self._modulo_activo
            )

            if sub_boton is not None:

                sub_boton.set_activo(
                    activo,
                )

            if activo and padre is not None:

                padres_activos.add(
                    id(padre),
                )

        for boton in self._botones:

            if boton is self._boton_submenu_abierto:

                continue

            boton.set_submenu_abierto(
                id(boton) in padres_activos,
            )

    def _seleccionar(
        self,
        modulo: str,
    ) -> None:



        self.modulo_seleccionado.emit(

            modulo,

        )


