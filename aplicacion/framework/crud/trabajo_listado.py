from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QObject, Signal


class TrabajoListado(QObject):
    """Ejecuta una consulta de listado fuera del hilo de UI."""

    terminado = Signal(
        object,
    )

    error = Signal(
        str,
    )

    def __init__(
        self,
        consulta: Callable[[], object],
    ):
        super().__init__()

        self._consulta = consulta

    def ejecutar(
        self,
    ) -> None:
        try:
            resultado = self._consulta()

            self.terminado.emit(
                resultado,
            )

        except Exception as exc:
            self.error.emit(
                str(
                    exc,
                ),
            )
