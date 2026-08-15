from __future__ import annotations

from .binding import FormBinding
from .builder import FormBuilder
from .campo_signals import conectar_cambio
from .events import FormEvents
from .form_context import FormContext
from .form_definition import FormDefinition
from .normalization_engine import NormalizationEngine
from .validation_engine import ValidationEngine
from .validators import ValidationError


class FormEngine:
    """
    Motor principal del Framework de Formularios.

    Coordina:

        • FormContext
        • FormBuilder
        • FormBinding
        • ValidationEngine
        • NormalizationEngine
        • FormEvents

    El Engine coordina los componentes,
    pero no crea widgets directamente.
    """

    # ==================================================
    # Inicialización
    # ==================================================

    def __init__(
        self,
        definition: type[FormDefinition],
    ):

        if definition is None:

            raise RuntimeError(
                "FormEngine requiere una FormDefinition."
            )

        self.definition = definition

        # --------------------------------------------------
        # Contexto compartido
        # --------------------------------------------------

        self.context = FormContext()

        self.context.engine = self

        self.context.formulario = definition

        # --------------------------------------------------
        # Builder
        # --------------------------------------------------

        self.builder = FormBuilder(
            definition,
            context=self.context,
        )

        # --------------------------------------------------
        # Layout
        # --------------------------------------------------

        self._layout = None

        # --------------------------------------------------
        # Binding
        #
        # Se crea después de construir los widgets.
        # --------------------------------------------------

        self.binding = None

        # --------------------------------------------------
        # Motores
        # --------------------------------------------------

        self.validation = ValidationEngine(
            definition
        )

        self.normalization = NormalizationEngine(
            definition
        )

        self.events = FormEvents()

        self._cambios_conectados = False

        # --------------------------------------------------
        # Registrar componentes en el contexto
        # --------------------------------------------------

        self.context.binding = self.binding

    # ==================================================
    # Construcción
    # ==================================================

    def construir(self):

        if self._layout is None:

            self._layout = self.builder.construir()

            self.binding = FormBinding(
                self.definition,
                self.builder.widgets,
            )

            self.context.binding = self.binding

            self._conectar_cambios_campos()

        return self._layout

    def _conectar_cambios_campos(
        self,
    ) -> None:

        if self._cambios_conectados:

            return

        if self.binding is None:

            return

        for campo in self.definition.obtener_campos():

            widget = self.builder.widgets.get(
                campo.nombre,
            )

            if widget is None:

                continue

            nombre = campo.nombre

            def _emitir_cambio(
                *,
                nombre_campo=nombre,
            ) -> None:

                valor = self.binding.valor(
                    nombre_campo,
                )

                self.emit(
                    f"campo:{nombre_campo}",
                    valor,
                )

                self.events.emitir_cambio(
                    nombre_campo,
                    valor,
                )

                self.context.limpiar_error(
                    nombre_campo,
                )

            conectar_cambio(
                widget,
                campo,
                _emitir_cambio,
            )

        self._cambios_conectados = True

    # ==================================================
    # Layout
    # ==================================================

    @property
    def layout(self):

        return self._layout

    # ==================================================
    # Widgets
    # ==================================================

    @property
    def widgets(self):

        return self.builder.widgets

    def widget(
        self,
        nombre: str,
    ):

        return self.builder.widget(
            nombre
        )

    # ==================================================
    # Binding
    # ==================================================

    def cargar(
        self,
        objeto,
    ):

        self._asegurar_construido()

        self.binding.cargar(
            objeto
        )

    def set_valor(
        self,
        nombre,
        valor,
    ):

        self._asegurar_construido()

        self.binding.set_valor(
            nombre,
            valor,
        )

    def valores(self):

        self._asegurar_construido()

        datos = self.binding.valores()

        datos = self.normalization.normalizar(
            datos
        )

        datos = self.normalization.normalizar(
            datos
        )

        errores = self.validation.errores(
            datos,
        )

        self.context.limpiar_errores()

        if errores:

            self.context.aplicar_errores(
                {
                    nombre: str(
                        error,
                    )
                    for nombre, error in errores.items()
                },
            )

            raise ValidationError(
                "\n".join(
                    str(
                        error,
                    )
                    for error in errores.values()
                ),
            )

        return datos

    def actualizar(
        self,
        objeto,
    ):

        self._asegurar_construido()

        return self.binding.actualizar(
            objeto,
            self.valores(),
        )

    # ==================================================
    # Asegurar construcción
    # ==================================================

    def _asegurar_construido(self):

        if self.binding is None:

            self.construir()

    # ==================================================
    # Eventos genéricos
    # ==================================================

    def on(
        self,
        evento,
        callback,
    ):

        self.events.on(
            evento,
            callback,
        )

    def off(
        self,
        evento,
        callback,
    ):

        self.events.off(
            evento,
            callback,
        )

    def emit(
        self,
        evento,
        *args,
        **kwargs,
    ):

        self.events.emit(
            evento,
            *args,
            **kwargs,
        )

    # ==================================================
    # Compatibilidad
    # ==================================================

    def al_guardar(
        self,
        callback,
    ):

        self.events.al_guardar(
            callback
        )

    def al_cancelar(
        self,
        callback,
    ):

        self.events.al_cancelar(
            callback
        )

    def al_cambiar(
        self,
        callback,
    ):

        self.events.al_cambiar(
            callback
        )

    def guardar(self):

        self.events.emitir_guardar()

    def cancelar(self):

        self.events.emitir_cancelar()

    def cambio(
        self,
        nombre,
        valor,
    ):

        self.events.emitir_cambio(
            nombre,
            valor,
        )

    def aplicar_modo(
        self,
        modo,
    ) -> None:
        from .modo import ModoFormulario

        self._asegurar_construido()

        for campo in self.definition.obtener_campos():
            widget = self.builder.widgets.get(
                campo.nombre,
            )

            if widget is None:
                continue

            solo_lectura = (
                campo.solo_lectura
                or modo
                == ModoFormulario.CONSULTA
            )

            if not solo_lectura:
                continue

            if hasattr(
                widget,
                "setReadOnly",
            ):
                widget.setReadOnly(
                    True,
                )
            elif hasattr(
                widget,
                "setEnabled",
            ):
                widget.setEnabled(
                    False,
                )