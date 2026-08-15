from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable


class TableEvents:
    """
    Administrador de eventos de la tabla.

    Responsabilidad única:

        • Registrar eventos
        • Eliminar eventos
        • Emitir eventos

    No conoce:

        • Qt
        • DataGrid
        • SQLAlchemy
        • CRUD
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
    # Compatibilidad
    # =====================================================

    def al_doble_click(
        self,
        callback,
    ):

        self.on(
            "doble_click",
            callback,
        )

    def al_seleccionar(
        self,
        callback,
    ):

        self.on(
            "seleccion",
            callback,
        )

    def al_actualizar(
        self,
        callback,
    ):

        self.on(
            "actualizar",
            callback,
        )

    def emitir_doble_click(
        self,
        registro,
    ):

        self.emit(
            "doble_click",
            registro,
        )

    def emitir_seleccion(
        self,
        registro,
    ):

        self.emit(
            "seleccion",
            registro,
        )

    def emitir_actualizar(self):

        self.emit(
            "actualizar",
        )