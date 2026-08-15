from __future__ import annotations

from PySide6.QtCore import QTimer, QObject, Signal

from aplicacion.integraciones.correo.servicio_correo_facturas import (
    ServicioCorreoFacturas,
)
from aplicacion.nucleo.configuracion import Configuracion


class ProgramadorCorreoFacturas(QObject):

    procesamiento_completado = Signal(object)

    _instancia: ProgramadorCorreoFacturas | None = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(
            self._ejecutar,
        )

    @classmethod
    def instancia(
        cls,
        parent=None,
    ) -> ProgramadorCorreoFacturas:
        if cls._instancia is None:
            cls._instancia = cls(parent)

        return cls._instancia

    @classmethod
    def habilitado(cls) -> bool:
        return ServicioCorreoFacturas.habilitado()

    def iniciar(self) -> None:
        if not self.habilitado():
            return

        config = (
            Configuracion.obtener(
                "correo",
                "facturas",
            )
            or {}
        )

        minutos = int(
            config.get(
                "intervalo_minutos",
                15,
            )
        )

        self._timer.start(
            max(
                minutos,
                1,
            )
            * 60
            * 1000,
        )

    def _ejecutar(self) -> None:
        resultado = (
            ServicioCorreoFacturas.procesar_buzon()
        )

        self.procesamiento_completado.emit(
            resultado,
        )

    def procesar_ahora(self) -> dict:
        return ServicioCorreoFacturas.procesar_buzon()
