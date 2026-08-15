from __future__ import annotations


REGISTRO_01_LONGITUD = 359
REGISTRO_02_LONGITUD = 693


def campo_numerico(
    valor: int | float | str,
    longitud: int,
) -> str:

    texto = str(
        int(
            round(
                float(valor or 0),
            ),
        ),
    )

    if len(texto) > longitud:

        texto = texto[-longitud:]

    return texto.rjust(
        longitud,
        "0",
    )


def campo_alfanumerico(
    valor: str,
    longitud: int,
) -> str:

    texto = str(
        valor or "",
    ).strip().upper()

    if len(texto) > longitud:

        texto = texto[:longitud]

    return texto.ljust(
        longitud,
        " ",
    )


def tarifa_pila(
    porcentaje: float,
) -> str:
    """
    Formato tarifa PILA: 7 dígitos (porcentaje con 5 decimales implícitos).
    Ej: 12% -> 0120000, 8.5% -> 0085000
    """

    return campo_numerico(
        int(
            round(
                float(porcentaje) * 1_000_000,
            ),
        ),
        7,
    )


class RegistroPilaBuilder:

    def __init__(
        self,
        longitud: int,
    ):

        self._longitud = longitud
        self._buffer = [
            " "
        ] * longitud

    def escribir(
        self,
        inicio: int,
        longitud: int,
        valor: str | int | float,
        *,
        numerico: bool = False,
    ) -> None:

        if numerico:

            texto = campo_numerico(
                valor,
                longitud,
            )

        else:

            texto = campo_alfanumerico(
                str(valor),
                longitud,
            )

        indice = inicio - 1

        for offset, caracter in enumerate(
            texto,
        ):

            if indice + offset >= self._longitud:

                break

            self._buffer[
                indice + offset
            ] = caracter

    def render(self) -> str:

        return "".join(
            self._buffer,
        )
