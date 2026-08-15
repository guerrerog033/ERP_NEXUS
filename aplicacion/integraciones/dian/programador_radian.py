from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QObject, QTimer, Signal

from aplicacion.integraciones.dian.servicio_eventos_radian import (
    ServicioEventosRadian,
)
from aplicacion.modulos.compras.facturas.repositorio_eventos_radian import (
    RepositorioFacturaCompraEventoRadian,
)
from aplicacion.nucleo.configuracion import Configuracion


@dataclass
class ResultadoProgramadorRadian:

    procesadas: int = 0
    exitosas: int = 0
    errores: list[str] = field(
        default_factory=list,
    )
    mensaje: str = ""


class ProgramadorRadian033(QObject):

    ejecucion_completada = Signal(
        object,
    )

    _instancia: ProgramadorRadian033 | None = None

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
            self._ejecutar,
        )

    @classmethod
    def instancia(
        cls,
        parent=None,
    ) -> ProgramadorRadian033:

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
                "radian",
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
                15,
                int(
                    config.get(
                        "intervalo_minutos",
                        60,
                    )
                    or 60,
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            return 60

    @classmethod
    def dias_aceptacion_tacita(cls) -> int:

        config = cls._config()

        try:

            return max(
                1,
                int(
                    config.get(
                        "dias_aceptacion_tacita",
                        5,
                    )
                    or 5,
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            return 5

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
            "ejecutar_al_iniciar",
            True,
        ):

            QTimer.singleShot(
                8000,
                self._ejecutar,
            )

    def detener(
        self,
    ) -> None:

        self._timer.stop()

    def ejecutar_ahora(
        self,
    ) -> ResultadoProgramadorRadian:

        resultado = self._procesar_pendientes()

        self.ejecucion_completada.emit(
            resultado,
        )

        return resultado

    def _ejecutar(
        self,
    ) -> None:

        if not self.modo_automatico_habilitado():

            return

        self.ejecutar_ahora()

    def _procesar_pendientes(
        self,
    ) -> ResultadoProgramadorRadian:

        config = self._config()

        exigir_031 = bool(
            config.get(
                "exigir_evento_031",
                True,
            ),
        )

        dias = self.dias_aceptacion_tacita()

        facturas = (
            RepositorioFacturaCompraEventoRadian
            .listar_facturas_pendientes_033(
                dias_plazo=dias,
            )
        )

        resultado = ResultadoProgramadorRadian()

        for factura in facturas:

            if exigir_031 and not (
                RepositorioFacturaCompraEventoRadian
                .existe_exitoso(
                    factura.id,
                    "031",
                )
            ):

                continue

            resultado.procesadas += 1

            evento = ServicioEventosRadian.procesar(
                factura.id,
                "033",
            )

            if evento.exito:

                resultado.exitosas += 1

            elif evento.error:

                resultado.errores.append(
                    f"{factura.numero}: {evento.error}",
                )

        resultado.mensaje = (
            f"RADIAN 033: {resultado.exitosas}/"
            f"{resultado.procesadas} enviados."
        )

        return resultado
