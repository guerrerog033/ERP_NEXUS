from __future__ import annotations

from abc import ABC, abstractmethod

from aplicacion.nucleo.configuracion import Configuracion


class PasarelaPagoBase(ABC):

    nombre: str = "base"

    @abstractmethod
    def crear_enlace_pago(
        self,
        *,
        referencia: str,
        valor: float,
        descripcion: str,
    ) -> dict:
        ...

    @abstractmethod
    def procesar_webhook(
        self,
        payload: dict,
    ) -> dict:
        ...


class PasarelaBold(PasarelaPagoBase):

    nombre = "bold"

    @classmethod
    def _config(cls) -> dict:
        return dict(
            Configuracion.obtener(
                "pagos",
                "bold",
            )
            or {},
        )

    def crear_enlace_pago(
        self,
        *,
        referencia: str,
        valor: float,
        descripcion: str,
    ) -> dict:
        config = self._config()

        return {
            "pasarela": "bold",
            "referencia": referencia,
            "valor": valor,
            "url": (
                config.get(
                    "url_base",
                    "https://checkout.bold.co",
                )
                + f"?ref={referencia}&amount={int(valor)}"
            ),
            "descripcion": descripcion,
        }

    def procesar_webhook(
        self,
        payload: dict,
    ) -> dict:
        from aplicacion.integraciones.pagos.servicio_recaudo import (
            ServicioRecaudo,
        )

        referencia = payload.get(
            "reference",
            "",
        )
        valor = float(
            payload.get(
                "amount",
                0,
            )
        )

        return ServicioRecaudo.aplicar_pago(
            referencia=referencia,
            valor=valor,
            pasarela="bold",
        )


class PasarelaWompi(PasarelaPagoBase):

    nombre = "wompi"

    def crear_enlace_pago(
        self,
        *,
        referencia: str,
        valor: float,
        descripcion: str,
    ) -> dict:
        config = dict(
            Configuracion.obtener(
                "pagos",
                "wompi",
            )
            or {},
        )

        return {
            "pasarela": "wompi",
            "referencia": referencia,
            "valor": valor,
            "url": (
                config.get(
                    "url_base",
                    "https://checkout.wompi.co/l",
                )
                + f"?ref={referencia}"
            ),
            "descripcion": descripcion,
        }

    def procesar_webhook(
        self,
        payload: dict,
    ) -> dict:
        from aplicacion.integraciones.pagos.servicio_recaudo import (
            ServicioRecaudo,
        )

        referencia = payload.get(
            "reference",
            "",
        )
        valor = float(
            payload.get(
                "amount_in_cents",
                0,
            )
            / 100,
        )

        return ServicioRecaudo.aplicar_pago(
            referencia=referencia,
            valor=valor,
            pasarela="wompi",
        )


PASARELAS = {
    "bold": PasarelaBold(),
    "wompi": PasarelaWompi(),
}


def obtener_pasarela(nombre: str) -> PasarelaPagoBase:
    pasarela = PASARELAS.get(
        str(nombre or "").lower(),
    )

    if pasarela is None:
        raise ValueError(
            f"Pasarela no soportada: {nombre}",
        )

    return pasarela
