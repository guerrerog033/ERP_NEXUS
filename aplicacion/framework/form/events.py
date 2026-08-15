from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable


class FormEvents:
    """
    Administrador de eventos del formulario.

    Responsabilidad única:

        • Registrar eventos
        • Eliminar eventos
        • Emitir eventos

    No conoce:

        • Qt
        • Widgets
        • SQLAlchemy
        • Formularios
    """

    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(self):

        self._eventos = defaultdict(list)

    # =====================================================
    # Registrar
    # =====================================================

    def on(
        self,
        evento: str,
        callback: Callable,
    ):

        if callback not in self._eventos[evento]:

            self._eventos[evento].append(
                callback
            )

    # =====================================================
    # Eliminar
    # =====================================================

    def off(
        self,
        evento: str,
        callback: Callable,
    ):

        callbacks = self._eventos.get(
            evento
        )

        if callbacks is None:

            return

        try:

            callbacks.remove(
                callback
            )

        except ValueError:

            pass

    # =====================================================
    # Limpiar
    # =====================================================

    def clear(
        self,
        evento: str | None = None,
    ):

        if evento is None:

            self._eventos.clear()

            return

        self._eventos.pop(
            evento,
            None,
        )

    # =====================================================
    # Emitir
    # =====================================================

    def emit(
        self,
        evento: str,
        *args,
        **kwargs,
    ):

        for callback in tuple(

            self._eventos.get(
                evento,
                (),
            )

        ):

            callback(
                *args,
                **kwargs,
            )

    # =====================================================
    # Eventos de formulario
    # =====================================================

    def al_guardar(
        self,
        callback: Callable,
    ) -> None:

        self.on(
            "guardar",
            callback,
        )

    def al_cancelar(
        self,
        callback: Callable,
    ) -> None:

        self.on(
            "cancelar",
            callback,
        )

    def al_cambiar(
        self,
        callback: Callable,
    ) -> None:

        self.on(
            "cambio",
            callback,
        )

    def emitir_guardar(
        self,
    ) -> None:

        self.emit(
            "guardar",
        )

    def emitir_cancelar(
        self,
    ) -> None:

        self.emit(
            "cancelar",
        )

    def emitir_cambio(
        self,
        nombre: str,
        valor,
    ) -> None:

        self.emit(
            "cambio",
            nombre,
            valor,
        )