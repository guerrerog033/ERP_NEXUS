"""
Barra de menú clásica de escritorio (Archivo, Comercial, Maestros…),
como en Siigo Pyme y World Office. Se arma desde el mismo manifiesto
del menú lateral, así ambos muestran siempre los mismos módulos y
respetan los permisos del rol.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMenuBar

from aplicacion.framework.menu_manifest import (
    MODULO_INICIO,
    grupos_visibles,
)
from aplicacion.framework.ui.iconos import icono_accion, icono_modulo


class BarraMenu(QMenuBar):

    modulo_seleccionado = Signal(str)

    # Acciones generales que resuelve el Dashboard.
    accion_solicitada = Signal(str)

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self.setObjectName(
            "BarraMenu",
        )

        self.setNativeMenuBar(
            False,
        )

        self._construir()

    # -----------------------------------------------------

    def _accion(
        self,
        menu,
        texto: str,
        clave: str,
        *,
        atajo: str | None = None,
        icono=None,
    ):

        accion = menu.addAction(
            texto,
        )

        if icono is not None:

            accion.setIcon(
                icono,
            )

        if atajo:

            # Solo se muestra como recordatorio; los atajos reales
            # los registra cada pantalla (evita choques).
            accion.setText(
                f"{texto}\t{QKeySequence(atajo).toString(QKeySequence.SequenceFormat.NativeText)}",
            )

        accion.triggered.connect(
            lambda _=False, c=clave: self.accion_solicitada.emit(
                c,
            ),
        )

        return accion

    def _modulo(
        self,
        menu,
        texto: str,
        modulo_id: str,
        icono=None,
    ):

        accion = menu.addAction(
            texto,
        )

        if icono is not None:

            accion.setIcon(
                icono,
            )

        accion.triggered.connect(
            lambda _=False, m=modulo_id: self.modulo_seleccionado.emit(
                m,
            ),
        )

        return accion

    def _construir(
        self,
    ) -> None:

        archivo = self.addMenu(
            "&Archivo",
        )

        self._modulo(
            archivo,
            "Inicio",
            MODULO_INICIO,
            icono_modulo("inicio", tamano=16),
        )

        self._accion(
            archivo,
            "Buscar módulo…",
            "buscar_modulo",
            atajo="Ctrl+K",
            icono=icono_accion("buscar", tamano=16),
        )

        archivo.addSeparator()

        self._accion(
            archivo,
            "Cerrar sesión",
            "cerrar_sesion",
        )

        self._accion(
            archivo,
            "Salir",
            "salir",
            icono=icono_accion("salir", tamano=16),
        )

        for titulo_grupo, entradas in grupos_visibles():

            if not titulo_grupo:

                continue

            menu_grupo = self.addMenu(
                titulo_grupo,
            )

            for entrada in entradas:

                icono = icono_modulo(
                    entrada.get(
                        "icono",
                        "",
                    ),
                    tamano=16,
                )

                submenu = entrada.get(
                    "submenu",
                )

                if submenu:

                    menu_sub = menu_grupo.addMenu(
                        icono,
                        entrada["titulo"],
                    )

                    for texto, modulo_id in submenu:

                        self._modulo(
                            menu_sub,
                            texto,
                            modulo_id,
                        )

                    continue

                self._modulo(
                    menu_grupo,
                    entrada["titulo"],
                    entrada.get(
                        "modulo",
                        "",
                    ),
                    icono,
                )

        ventana = self.addMenu(
            "&Ventana",
        )

        self._accion(
            ventana,
            "Pestaña siguiente",
            "pestana_siguiente",
            atajo="Ctrl+Tab",
        )

        self._accion(
            ventana,
            "Pestaña anterior",
            "pestana_anterior",
            atajo="Ctrl+Shift+Tab",
        )

        ventana.addSeparator()

        self._accion(
            ventana,
            "Cerrar pestaña",
            "cerrar_pestana",
            atajo="Ctrl+W",
            icono=icono_accion("cerrar", tamano=16),
        )

        self._accion(
            ventana,
            "Cerrar todas las pestañas",
            "cerrar_todas",
        )

        ayuda = self.addMenu(
            "A&yuda",
        )

        self._accion(
            ayuda,
            "Atajos de teclado",
            "ayuda",
            atajo="F1",
            icono=icono_accion("ayuda", tamano=16),
        )

        self._accion(
            ayuda,
            "Acerca de",
            "acerca_de",
        )
