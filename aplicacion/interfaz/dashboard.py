from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from aplicacion.framework.app_context import AppContext
from aplicacion.framework.menu_manifest import (
    MODULO_INICIO,
    MODULO_PENDIENTE,
    modulo_accesible,
)
from aplicacion.framework.modulo_manager import ModuloManager

from aplicacion.interfaz.area_trabajo import AreaTrabajo
from aplicacion.interfaz.barra_estado import BarraEstado
from aplicacion.interfaz.barra_lateral import BarraLateral
from aplicacion.interfaz.barra_menu import BarraMenu
from aplicacion.interfaz.barra_teclas import BarraTeclas
from aplicacion.interfaz.barra_superior import BarraSuperior
from aplicacion.interfaz.buscador_modulos import BuscadorModulos
from aplicacion.interfaz.navegacion_usuario import NavegacionUsuario
from aplicacion.nucleo.configuracion import Configuracion


class Dashboard(QWidget):

    TITULO = "ERP NEXUS"

    cerrar_sesion_solicitado = Signal()

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        usuario,
        *,
        embebido: bool = False,
    ):

        super().__init__()

        self._embebido = embebido
        self.usuario = usuario

        from aplicacion.autenticacion.servicios import (
            cargar_permisos_usuario,
        )

        cargar_permisos_usuario(
            usuario,
        )

        from aplicacion.nucleo.sesion import Sesion

        Sesion.iniciar(
            usuario,
        )

        from aplicacion.nucleo.auditoria import Auditoria

        Auditoria.registrar(
            usuario,
            "login",
            "Inicio de sesión exitoso.",
            modulo="Seguridad",
            exito=True,
        )

        self.setObjectName(
            "Dashboard"
        )

        # Pinta el fondo claro del tema; sin esto se veía el azul
        # oscuro de la ventana del login alrededor del contenido.
        from aplicacion.recursos.estilos.tema import (
            habilitar_fondo_qss,
        )

        habilitar_fondo_qss(
            self,
        )

        self.setWindowTitle(
            self._titulo_ventana()
        )

        if not embebido:

            self.showMaximized()

        self._crear_componentes()

        self._crear_layout()

        self._crear_contexto()

    def _titulo_ventana(
        self,
    ) -> str:

        empresa = (
            Configuracion.obtener(
                "empresa",
                "nombre",
            )
            or self.TITULO
        )

        return (
            f"{empresa} - "
            f"{Configuracion.obtener('erp', 'nombre') or self.TITULO}"
        )

    # =====================================================
    # Componentes
    # =====================================================

    def _crear_componentes(
        self,
    ):

        self.barra_menu = BarraMenu(
            self,
        )

        self.barra_superior = BarraSuperior(
            self.usuario
        )

        self.barra_teclas = BarraTeclas()

        self.barra_lateral = BarraLateral()

        self.area_trabajo = AreaTrabajo()

        self.barra_estado = BarraEstado(
            self.usuario
        )

        self.modulos = ModuloManager(
            self.area_trabajo
        )

        self.barra_lateral.modulo_seleccionado.connect(
            self.modulo_seleccionado
        )

        self.area_trabajo.inicio.modulo_solicitado.connect(
            self.modulo_seleccionado,
        )

        self.barra_menu.modulo_seleccionado.connect(
            self.modulo_seleccionado,
        )

        self.barra_menu.accion_solicitada.connect(
            self._accion_menu,
        )

        self.barra_superior.modulo_solicitado.connect(
            self.modulo_seleccionado,
        )

        self.area_trabajo.currentChanged.connect(
            self._pestana_cambiada,
        )

    # =====================================================
    # Layout
    # =====================================================

    def _crear_layout(
        self,
    ):

        contenido = QHBoxLayout()

        contenido.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        contenido.setSpacing(
            0
        )

        contenido.addWidget(
            self.barra_lateral
        )

        contenido.addWidget(
            self.area_trabajo,
            1,
        )

        principal = QVBoxLayout()

        principal.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        principal.setSpacing(
            0
        )

        principal.addWidget(
            self.barra_menu
        )

        principal.addWidget(
            self.barra_superior
        )

        principal.addLayout(
            contenido,
            1,
        )

        principal.addWidget(
            self.barra_teclas
        )

        principal.addWidget(
            self.barra_estado
        )

        self.setLayout(
            principal
        )

    # =====================================================
    # Contexto global
    # =====================================================

    def _crear_contexto(
        self,
    ):

        AppContext.dashboard = self

        AppContext.area_trabajo = (
            self.area_trabajo
        )

        AppContext.usuario = (
            self.usuario
        )

        AppContext.barra_estado = (
            self.barra_estado
        )

        self.barra_superior.cerrar_sesion.connect(
            self._cerrar_sesion,
        )

        self.barra_superior.busqueda_solicitada.connect(
            self._abrir_buscador_con_texto,
        )

        self.navegacion = NavegacionUsuario(
            self.usuario.id,
        )

        AppContext.navegacion = (
            self.navegacion
        )

        self.barra_lateral.actualizar_accesos_rapidos()

        self.barra_lateral.marcar_activo(
            MODULO_INICIO,
        )

        from aplicacion.integraciones.dian.programador_recepcion import (
            ProgramadorRecepcionCompras,
        )

        ProgramadorRecepcionCompras.instancia(
            self,
        ).iniciar()

        from aplicacion.integraciones.dian.programador_radian import (
            ProgramadorRadian033,
        )

        ProgramadorRadian033.instancia(
            self,
        ).iniciar()

        from aplicacion.api.servidor import (
            ServidorApiErp,
        )

        ServidorApiErp.iniciar()

        from aplicacion.integraciones.correo.programador_correo import (
            ProgramadorCorreoFacturas,
        )

        ProgramadorCorreoFacturas.instancia(
            self,
        ).iniciar()

        atajo_buscador = QShortcut(
            QKeySequence(
                "Ctrl+K",
            ),
            self,
        )

        atajo_buscador.activated.connect(
            self._activar_busqueda,
        )

        from aplicacion.framework.ui.atajos import (
            instalar_filtro_teclado,
            mostrar_ayuda,
            registrar_atajos,
        )

        instalar_filtro_teclado()

        registrar_atajos(
            self,
            (
                ("F1", lambda: mostrar_ayuda(self)),
                ("Ctrl+W", self.area_trabajo.cerrar_actual),
                ("Ctrl+Tab", lambda: self._cambiar_pestana(1)),
                ("Ctrl+Shift+Tab", lambda: self._cambiar_pestana(-1)),
            ),
            contexto=Qt.ShortcutContext.WindowShortcut,
        )

        from aplicacion.framework.ui.atajos import mostrar_ayuda as _ayuda

        self.barra_teclas.set_teclas_generales(
            (
                ("F1", "Ayuda", lambda: _ayuda(self)),
                ("Ctrl+K", "Buscar módulo", self._activar_busqueda),
                ("Ctrl+W", "Cerrar pestaña", self.area_trabajo.cerrar_actual),
            ),
        )

        self.area_trabajo.mostrar_inicio()

        self._pestana_cambiada(
            self.area_trabajo.currentIndex(),
        )

    # =====================================================
    # Pestaña activa → barra de teclas y barra de estado
    # =====================================================

    def _pestana_cambiada(
        self,
        indice: int,
    ) -> None:

        from aplicacion.framework.ui.colores_modulo import (
            color_modulo,
            nombre_area,
        )

        widget = self.area_trabajo.widget(
            indice,
        )

        self.barra_teclas.actualizar_desde(
            widget,
        )

        modulo_id = getattr(
            widget,
            "_modulo_id",
            None,
        )

        if indice <= 0 or widget is None:

            self.barra_estado.set_modulo(
                "Inicio",
            )

            self.barra_estado.set_pantalla(
                "",
            )

        else:

            self.barra_estado.set_modulo(
                nombre_area(modulo_id or "") or "ERP",
                color_modulo(modulo_id or ""),
            )

            self.barra_estado.set_pantalla(
                self.area_trabajo.tabText(
                    indice,
                ),
            )

        self.barra_estado.set_registro(
            "",
        )

        if modulo_id:

            self.barra_lateral.marcar_activo(
                modulo_id,
            )

    def actualizar_barra_teclas(
        self,
    ) -> None:

        self.barra_teclas.actualizar_desde(
            self.area_trabajo.currentWidget(),
        )

    def _accion_menu(
        self,
        clave: str,
    ) -> None:

        from aplicacion.framework.ui.atajos import mostrar_ayuda

        acciones = {
            "buscar_modulo": self._activar_busqueda,
            "cerrar_sesion": self._cerrar_sesion,
            "salir": self._salir,
            "pestana_siguiente": lambda: self._cambiar_pestana(1),
            "pestana_anterior": lambda: self._cambiar_pestana(-1),
            "cerrar_pestana": self.area_trabajo.cerrar_actual,
            "cerrar_todas": self._cerrar_todas,
            "ayuda": lambda: mostrar_ayuda(self),
            "acerca_de": self._acerca_de,
        }

        accion = acciones.get(
            clave,
        )

        if accion is not None:

            accion()

    def _cerrar_todas(
        self,
    ) -> None:

        for indice in range(
            self.area_trabajo.count() - 1,
            0,
            -1,
        ):

            self.area_trabajo.cerrar_pestana(
                indice,
            )

    def _salir(
        self,
    ) -> None:

        ventana = self.window()

        if ventana is not None:

            ventana.close()

    def _acerca_de(
        self,
    ) -> None:

        nombre = (
            Configuracion.obtener(
                "erp",
                "nombre",
            )
            or self.TITULO
        )

        empresa = (
            Configuracion.obtener(
                "empresa",
                "nombre",
            )
            or ""
        )

        QMessageBox.about(
            self,
            f"Acerca de {nombre}",
            f"<b>{nombre}</b><br>Sistema contable y administrativo"
            + (
                f"<br><br>Licenciado a: {empresa}"
                if empresa
                else ""
            ),
        )

    def _cambiar_pestana(
        self,
        paso: int,
    ) -> None:

        area = self.area_trabajo

        visibles = [
            indice
            for indice in range(
                area.count(),
            )
            if area.isTabVisible(
                indice,
            )
        ]

        if not visibles:

            return

        actual = area.currentIndex()

        posicion = (
            visibles.index(actual)
            if actual in visibles
            else 0
        )

        area.setCurrentIndex(
            visibles[
                (posicion + paso) % len(visibles)
            ],
        )

    def _activar_busqueda(
        self,
    ) -> None:

        self.barra_superior.enfocar_busqueda()

    def _abrir_buscador(
        self,
        texto_inicial: str = "",
    ) -> None:

        dialogo = BuscadorModulos(
            texto_inicial,
            self,
        )

        dialogo.modulo_seleccionado.connect(
            self.modulo_seleccionado,
        )

        dialogo.exec()

    def _abrir_buscador_con_texto(
        self,
        texto: str,
    ) -> None:

        self._abrir_buscador(
            texto,
        )

    def preparar_cierre(
        self,
    ) -> None:

        from aplicacion.integraciones.dian.programador_recepcion import (
            ProgramadorRecepcionCompras,
        )

        from aplicacion.api.servidor import (
            ServidorApiErp,
        )

        ProgramadorRecepcionCompras.instancia(
            self,
        ).detener()

        from aplicacion.integraciones.dian.programador_radian import (
            ProgramadorRadian033,
        )

        ProgramadorRadian033.instancia(
            self,
        ).detener()

        ServidorApiErp.detener()

        AppContext.dashboard = None
        AppContext.area_trabajo = None
        AppContext.barra_estado = None

    def _cerrar_sesion(
        self,
    ) -> None:

        from aplicacion.nucleo.permisos import (
            Permisos,
        )

        from aplicacion.nucleo.sesion import Sesion

        from aplicacion.nucleo.auditoria import Auditoria

        if self.usuario is not None:

            Auditoria.registrar(
                self.usuario,
                "logout",
                "Cierre de sesión.",
                modulo="Seguridad",
                exito=True,
            )

        Sesion.cerrar()

        Permisos.limpiar()

        AppContext.usuario = None

        AppContext.navegacion = None

        if self._embebido:

            self.cerrar_sesion_solicitado.emit()

            return

        from aplicacion.interfaz.login import Login

        self.close()

        login = Login()

        login.show()

    # =====================================================
    # Menú
    # =====================================================

    def modulo_seleccionado(
        self,
        nombre: str,
    ):

        if nombre != MODULO_PENDIENTE:

            self.barra_lateral.marcar_activo(
                nombre,
            )

        if nombre == MODULO_INICIO:

            self.area_trabajo.mostrar_inicio()

            return

        if nombre == MODULO_PENDIENTE:

            QMessageBox.information(
                self,
                "Información",
                "Este módulo estará disponible próximamente.",
            )

            return

        if not modulo_accesible(
            nombre,
        ):

            QMessageBox.warning(
                self,
                "Acceso denegado",
                "Su rol no tiene permiso "
                f"para abrir «{nombre}».",
            )

            return

        try:

            self.modulos.abrir(
                nombre
            )

        except Exception:

            import traceback

            print("=" * 60)

            print(
                f"ERROR AL ABRIR '{nombre}'"
            )

            traceback.print_exc()

    def menu_seleccionado(
        self,
        item,
        columna,
    ):

        self.modulo_seleccionado(
            item.text(0)
        )
