from PySide6.QtCore import Signal
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

        self.barra_superior = BarraSuperior(
            self.usuario
        )

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
            self.barra_superior
        )

        principal.addLayout(
            contenido,
            1,
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

        self.area_trabajo.mostrar_inicio()

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

        if nombre == MODULO_INICIO:

            self.area_trabajo.mostrar_inicio()

            self.navegacion.registrar_visita(
                nombre,
            )

            self.barra_lateral.actualizar_accesos_rapidos()

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

            self.navegacion.registrar_visita(
                nombre,
            )

            self.barra_lateral.actualizar_accesos_rapidos()

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
