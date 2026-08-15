from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal

from aplicacion.integraciones.dian.cliente_recepcion import (
    ClienteRecepcionDian,
)
from aplicacion.integraciones.dian.modelos_recepcion import (
    ResultadoSincronizacionCompras,
)
from aplicacion.integraciones.dian.servicio_recepcion import (
    ServicioRecepcionCompras,
)
from aplicacion.nucleo.configuracion import Configuracion


class ProgramadorRecepcionCompras(QObject):

    sincronizacion_completada = Signal(
        object,
    )

    _instancia: ProgramadorRecepcionCompras | None = None

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self._timer = QTimer(
            self,
        )

        self._timer.timeout.connect(
            self._ejecutar_sincronizacion,
        )

        self._ultimo_resultado: (
            ResultadoSincronizacionCompras | None
        ) = None

    @classmethod
    def instancia(
        cls,
        parent=None,
    ) -> ProgramadorRecepcionCompras:

        if cls._instancia is None:

            cls._instancia = cls(
                parent,
            )

        return cls._instancia

    @classmethod
    def _config(cls) -> dict:

        return dict(
            Configuracion.obtener(
                "dian",
                "recepcion_compras",
            )
            or {},
        )

    @classmethod
    def modo_automatico_habilitado(cls) -> bool:

        config = cls._config()

        return bool(
            config.get(
                "habilitado",
                False,
            )
            and config.get(
                "modo_automatico",
                False,
            )
        )

    @classmethod
    def intervalo_minutos(cls) -> int:

        config = cls._config()

        try:

            return max(
                5,
                int(
                    config.get(
                        "intervalo_minutos",
                        30,
                    )
                    or 30,
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            return 30

    def iniciar(
        self,
    ) -> None:

        if not self.modo_automatico_habilitado():

            return

        if not self._timer.isActive():

            self._timer.start(
                self.intervalo_minutos()
                * 60
                * 1000,
            )

        if self._config().get(
            "sincronizar_al_iniciar",
            True,
        ):

            QTimer.singleShot(
                3000,
                self._ejecutar_sincronizacion,
            )

    def detener(
        self,
    ) -> None:

        self._timer.stop()

    def sincronizar_ahora(
        self,
        *,
        silencioso: bool = False,
    ) -> ResultadoSincronizacionCompras:

        if not ClienteRecepcionDian.habilitado():

            resultado = ResultadoSincronizacionCompras(
                mensaje=(
                    "Recepción DIAN deshabilitada."
                ),
            )

            self._ultimo_resultado = resultado

            return resultado

        resultado = ServicioRecepcionCompras.sincronizar()

        self._ultimo_resultado = resultado

        self.sincronizacion_completada.emit(
            resultado,
        )

        return resultado

    def _ejecutar_sincronizacion(
        self,
    ) -> None:

        if not self.modo_automatico_habilitado():

            return

        self.sincronizar_ahora(
            silencioso=True,
        )

    @property
    def ultimo_resultado(
        self,
    ) -> ResultadoSincronizacionCompras | None:

        return self._ultimo_resultado
