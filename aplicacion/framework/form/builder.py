from __future__ import annotations

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
)

from .campo_contenedor import CampoContenedor
from .form_definition import FormDefinition
from .widget_factory import WidgetFactory


class FormBuilder:
    """
    Construye la interfaz visual de una FormDefinition.

    FormBuilder conoce:

        • FormDefinition
        • FieldGroup
        • Field
        • WidgetFactory
        • Qt

    No contiene lógica de negocio ni de persistencia.
    """

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(
        self,
        definition: type[FormDefinition],
        context=None,
    ):

        if definition is None:

            raise RuntimeError(
                "FormBuilder requiere una FormDefinition."
            )

        self.definition = definition

        self.context = context

        self.widgets: dict[str, object] = {}

    # =====================================================
    # Crear Widget
    # =====================================================

    def _crear_widget(
        self,
        campo,
    ):

        widget = WidgetFactory.crear(
            campo,
            self.context,
        )

        self.widgets[campo.nombre] = widget

        if self.context is not None:

            self.context.registrar_widget(
                campo.nombre,
                widget,
            )

        return widget

    def _envolver_campo(
        self,
        campo,
        widget,
    ):

        contenedor = CampoContenedor(
            widget,
        )

        if self.context is not None:

            self.context.registrar_campo_contenedor(
                campo.nombre,
                contenedor,
            )

        return contenedor

    # =====================================================
    # Construcción principal
    # =====================================================

    def construir(self):

        grupos = self.definition.obtener_grupos()

        if not grupos:

            layout = QVBoxLayout()

            layout.setContentsMargins(
                20,
                20,
                20,
                20,
            )

            return layout

        # -------------------------------------------------
        # Formulario simple sin grupos
        # -------------------------------------------------

        if (
            len(grupos) == 1
            and grupos[0].titulo == ""
        ):

            layout = QFormLayout()

            layout.setContentsMargins(
                20,
                20,
                20,
                20,
            )

            layout.setHorizontalSpacing(24)

            layout.setVerticalSpacing(14)

            layout.setFieldGrowthPolicy(
                QFormLayout.ExpandingFieldsGrow
            )

            self._agregar_campos(
                layout,
                grupos[0].campos,
            )

            return layout

        # -------------------------------------------------
        # Layout personalizado
        # -------------------------------------------------

        if getattr(
            self.definition,
            "layout",
            None,
        ) is not None:

            return self._construir_layout()

        # -------------------------------------------------
        # Layout vertical por grupos
        # -------------------------------------------------

        return self._construir_vertical()

    # =====================================================
    # Layout Vertical
    # =====================================================

    def _construir_vertical(self):

        principal = QVBoxLayout()

        principal.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        principal.setSpacing(20)

        for grupo in self.definition.obtener_grupos():

            if not grupo.visible:
                continue

            principal.addWidget(
                self._crear_grupo(grupo)
            )

        return principal

    # =====================================================
    # Layout Personalizado
    # =====================================================

    def _construir_layout(self):

        configuracion = self.definition.layout

        principal = QHBoxLayout()

        principal.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        principal.setSpacing(
            configuracion.separacion,
        )

        separacion_grupos = getattr(
            configuracion,
            "separacion_grupos",
            20,
        )

        grupos = {
            grupo.titulo: grupo
            for grupo
            in self.definition.obtener_grupos()
        }

        for indice, columna in enumerate(
            configuracion.columnas
        ):

            columna_layout = QVBoxLayout()

            columna_layout.setSpacing(
                separacion_grupos,
            )

            for nombre in columna:

                grupo = grupos.get(
                    nombre
                )

                if grupo is None:
                    continue

                if not grupo.visible:
                    continue

                columna_layout.addWidget(
                    self._crear_grupo(grupo)
                )

            columna_layout.addStretch()

            factor = 1

            if (
                indice
                < len(
                    configuracion.proporcion
                )
            ):

                factor = (
                    configuracion.proporcion[
                        indice
                    ]
                )

            principal.addLayout(
                columna_layout,
                factor,
            )

        return principal

    # =====================================================
    # Crear Grupo
    # =====================================================

    def _crear_grupo(
        self,
        grupo,
    ):

        groupbox = QGroupBox(
            grupo.titulo
        )

        groupbox.setObjectName(
            "FormGroupBox",
        )

        groupbox.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum,
        )

        groupbox.setVisible(
            grupo.visible
        )

        # -------------------------------------------------
        # Una columna
        # -------------------------------------------------

        if grupo.columnas <= 1:

            layout = QFormLayout()

            layout.setContentsMargins(
                16,
                16,
                16,
                16,
            )

            layout.setHorizontalSpacing(
                26
            )

            layout.setVerticalSpacing(
                10,
            )

            layout.setLabelAlignment(
                Qt.AlignRight
                | Qt.AlignVCenter
            )

            layout.setFieldGrowthPolicy(
                QFormLayout.ExpandingFieldsGrow
            )

            self._agregar_campos(
                layout,
                grupo.campos,
            )

            groupbox.setLayout(
                layout
            )

            return groupbox

        # -------------------------------------------------
        # Varias columnas
        # -------------------------------------------------

        layout = QGridLayout()

        layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        layout.setHorizontalSpacing(
            28
        )

        layout.setVerticalSpacing(
            10,
        )

        fila = 0
        columna = 0

        for campo in grupo.campos:

            if not campo.visible:
                continue

            widget = self._envolver_campo(
                campo,
                self._crear_widget(
                    campo,
                ),
            )

            control = self._control_widget(
                widget,
            )

            if campo.ocupa_fila_completa:

                if hasattr(
                    control,
                    "setText",
                ):

                    control.setText(
                        getattr(
                            campo,
                            "texto",
                            campo.etiqueta,
                        )
                    )

                layout.addWidget(
                    widget,
                    fila,
                    columna * 2,
                    1,
                    2,
                )

                fila += 1

                columna = 0

                continue

            etiqueta = self._crear_etiqueta(
                campo,
            )

            layout.addWidget(
                etiqueta,
                fila,
                columna * 2,
            )

            layout.addWidget(
                widget,
                fila,
                columna * 2 + 1,
            )

            self._ajustar_ancho_campo(
                campo,
                widget,
            )

            columna += 1

            if columna >= grupo.columnas:

                columna = 0

                fila += 1

        groupbox.setLayout(
            layout
        )

        return groupbox

    def _crear_etiqueta(
        self,
        campo,
    ) -> QLabel:

        etiqueta = QLabel()

        if campo.requerido_dian:

            etiqueta.setText(
                campo.etiqueta_html,
            )

            etiqueta.setTextFormat(
                Qt.RichText,
            )

        else:

            etiqueta.setText(
                campo.etiqueta,
            )

        etiqueta.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter,
        )

        return etiqueta

    def _control_widget(
        self,
        widget,
    ):

        control = getattr(
            widget,
            "control",
            widget,
        )

        return control

    def _ajustar_ancho_campo(
        self,
        campo,
        widget,
    ):

        control = self._control_widget(
            widget,
        )

        maximo = getattr(
            campo,
            "longitud_maxima",
            None,
        )

        if maximo is not None and maximo <= 4:

            control.setFixedWidth(
                72,
            )

            control.setSizePolicy(
                QSizePolicy.Fixed,
                QSizePolicy.Fixed,
            )

            return

        if hasattr(
            control,
            "setMinimumWidth",
        ):

            control.setMinimumWidth(
                200,
            )

        if hasattr(
            control,
            "setMaximumWidth",
        ):

            control.setMaximumWidth(
                280,
            )

        control.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

    # =====================================================
    # Agregar Campos
    # =====================================================

    def _agregar_campos(
        self,
        layout,
        campos,
    ):

        for campo in campos:

            if not campo.visible:
                continue

            widget = self._envolver_campo(
                campo,
                self._crear_widget(
                    campo,
                ),
            )

            control = self._control_widget(
                widget,
            )

            if campo.ocupa_fila_completa:

                if hasattr(
                    control,
                    "setText",
                ):

                    control.setText(
                        getattr(
                            campo,
                            "texto",
                            campo.etiqueta,
                        )
                    )

                layout.addRow(
                    "",
                    widget,
                )

                continue

            if hasattr(
                control,
                "setPlaceholderText",
            ):

                control.setPlaceholderText(
                    campo.placeholder or ""
                )

            self._ajustar_ancho_campo(
                campo,
                widget,
            )

            if campo.etiqueta_visible:

                layout.addRow(
                    self._crear_etiqueta(
                        campo,
                    ),
                    widget,
                )

            else:

                layout.addRow(
                    "",
                    widget,
                )

    # =====================================================
    # Obtener Widget
    # =====================================================

    def widget(
        self,
        nombre: str,
    ):

        return self.widgets.get(
            nombre
        )