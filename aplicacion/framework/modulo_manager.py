from aplicacion.framework.modulos import MODULOS
from aplicacion.framework.menu_manifest import (
    modulo_accesible,
)
from aplicacion.framework.ui.module_shell import (
    ModuleShellPage,
)


class ModuloManager:

    def __init__(self, area_trabajo):

        self.area_trabajo = area_trabajo

    # ==========================================================
    # Abrir módulo
    # ==========================================================

    def abrir(self, nombre):

        if nombre not in MODULOS:

            return

        if not modulo_accesible(
            nombre,
        ):

            return

        clase = MODULOS[nombre]

        titulo_visible = getattr(
            clase,
            "titulo",
            nombre,
        )

        # Si ya existe la pestaña, solo activarla
        for i in range(self.area_trabajo.count()):

            if self.area_trabajo.tabText(i) == titulo_visible:

                self.area_trabajo.setCurrentIndex(i)
                return

        modulo = clase()

        # Crear página contenedora
        pagina = ModuleShellPage(
            titulo=titulo_visible,
            subtitulo=f"Administración de {titulo_visible.lower()}"
        )

        pagina.setContenido(modulo)

        self.area_trabajo.abrir(
            pagina,
            titulo_visible,
        )
