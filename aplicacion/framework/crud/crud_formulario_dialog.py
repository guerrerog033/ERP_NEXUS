from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QScrollArea,
    QVBoxLayout,
)


class CrudFormularioDialog:
    """
    Formularios de alta/edición en ventana modal.

    Fase 5 UI: la lista permanece en pestaña del área de trabajo;
    crear y editar abren un QDialog modal (no una pestaña nueva).
    """

    formulario_en_modal: bool = True

    titulo_singular: str | None = None

    def usar_formulario_modal(
        self,
    ) -> bool:

        return bool(
            getattr(
                self,
                "formulario_en_modal",
                True,
            ),
        )

    def _ventana_padre_formulario(
        self,
    ):

        return self

    def _icono_dialogo_formulario(
        self,
    ) -> QIcon | None:

        return None

    def _margen_dialogo_formulario(
        self,
    ) -> int:

        return 32

    def _limites_dialogo_formulario(
        self,
        ancho: int,
        alto: int,
    ) -> tuple[
        tuple[int, int],
        tuple[int, int] | None,
    ]:

        min_ancho = min(
            ancho,
            640,
        )

        min_alto = min(
            alto,
            480,
        )

        return (
            (min_ancho, min_alto),
            None,
        )

    def _tamanio_dialogo_formulario(
        self,
        formulario,
    ) -> tuple[int, int]:

        margen = self._margen_dialogo_formulario()

        ancho_disponible = max(
            640,
            self.width() - margen,
        )

        alto_disponible = max(
            480,
            self.height() - margen,
        )

        ancho = min(
            getattr(
                formulario,
                "ancho",
                900,
            ),
            ancho_disponible,
        )

        alto = min(
            getattr(
                formulario,
                "alto",
                700,
            ),
            alto_disponible,
        )

        return ancho, alto

    def _titulo_dialogo_formulario(
        self,
        id_registro=None,
        *,
        modo=None,
    ) -> str:

        from aplicacion.framework.form.modo import (
            ModoFormulario,
            resolver_modo,
        )

        modo_resuelto = resolver_modo(
            modo,
            id_registro,
        )

        nombre = (
            getattr(
                self,
                "titulo_singular",
                None,
            )
            or getattr(
                self,
                "titulo",
                "Registro",
            )
        )

        if modo_resuelto == ModoFormulario.CONSULTA:
            return f"Consultar {nombre}"

        if modo_resuelto == ModoFormulario.EDICION:
            return f"Editar {nombre}"

        return f"Nuevo {nombre}"

    def _invocar_titulo_dialogo_formulario(
        self,
        id_registro=None,
        *,
        modo=None,
    ) -> str:

        import inspect

        from aplicacion.framework.form.modo import (
            ModoFormulario,
            resolver_modo,
        )

        parametros = inspect.signature(
            self._titulo_dialogo_formulario,
        ).parameters

        if "modo" in parametros:

            return self._titulo_dialogo_formulario(
                id_registro,
                modo=modo,
            )

        titulo = self._titulo_dialogo_formulario(
            id_registro,
        )

        if (
            resolver_modo(
                modo,
                id_registro,
            )
            == ModoFormulario.CONSULTA
            and titulo.startswith(
                "Editar ",
            )
        ):

            return titulo.replace(
                "Editar ",
                "Consultar ",
                1,
            )

        return titulo

    def _mostrar_dialogo_formulario(
        self,
        id_registro=None,
        *,
        modo=None,
    ) -> None:

        ventana = QDialog(
            self._ventana_padre_formulario(),
        )

        ventana.setWindowTitle(
            self._invocar_titulo_dialogo_formulario(
                id_registro,
                modo=modo,
            ),
        )

        icono = self._icono_dialogo_formulario()

        if icono is not None:

            ventana.setWindowIcon(
                icono,
            )

        ventana.setModal(
            True,
        )

        formulario = self.crear_formulario(
            id_registro=id_registro,
            parent=ventana,
            modo=modo,
        )

        ancho, alto = self._tamanio_dialogo_formulario(
            formulario,
        )

        ventana.resize(
            ancho,
            alto,
        )

        (
            minimo,
            maximo,
        ) = self._limites_dialogo_formulario(
            ancho,
            alto,
        )

        ventana.setMinimumSize(
            *minimo,
        )

        if maximo is not None:

            ventana.setMaximumSize(
                *maximo,
            )

        layout = QVBoxLayout(
            ventana,
        )

        layout.setContentsMargins(
            6,
            6,
            6,
            6,
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True,
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame,
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        )

        scroll.setWidget(
            formulario,
        )

        layout.addWidget(
            scroll,
        )

        formulario.guardado.connect(
            self.cargar_datos,
        )

        formulario.cerrar.connect(
            ventana.accept,
        )

        ventana.exec()

        formulario.deleteLater()

    def nuevo(
        self,
    ) -> None:

        if not self.usar_formulario_modal():

            super().nuevo()

            return

        self._mostrar_dialogo_formulario()

    def editar(
        self,
    ) -> None:

        if not self.usar_formulario_modal():

            super().editar()

            return

        id_registro = (
            self.obtener_id_seleccionado()
        )

        if id_registro is None:

            self.mostrar_error(
                "Seleccione un registro.",
            )

            return

        self._mostrar_dialogo_formulario(
            id_registro=id_registro,
        )
