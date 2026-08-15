from __future__ import annotations

_UNIDADES = (
    "",
    "UN",
    "DOS",
    "TRES",
    "CUATRO",
    "CINCO",
    "SEIS",
    "SIETE",
    "OCHO",
    "NUEVE",
    "DIEZ",
    "ONCE",
    "DOCE",
    "TRECE",
    "CATORCE",
    "QUINCE",
    "DIECISÉIS",
    "DIECISIETE",
    "DIECIOCHO",
    "DIECINUEVE",
)

_DECENAS = (
    "",
    "",
    "VEINTE",
    "TREINTA",
    "CUARENTA",
    "CINCUENTA",
    "SESENTA",
    "SETENTA",
    "OCHENTA",
    "NOVENTA",
)

_CENTENAS = (
    "",
    "CIENTO",
    "DOSCIENTOS",
    "TRESCIENTOS",
    "CUATROCIENTOS",
    "QUINIENTOS",
    "SEISCIENTOS",
    "SETECIENTOS",
    "OCHOCIENTOS",
    "NOVECIENTOS",
)


def _letras_hasta_99(
    numero: int,
) -> str:

    if numero < 20:

        return _UNIDADES[
            numero
        ]

    if numero < 30:

        if numero == 20:

            return "VEINTE"

        return (
            "VEINTI"
            + _UNIDADES[
                numero - 20
            ]
        ).replace(
            "VEINTIUN",
            "VEINTIÚN",
        )

    decena = numero // 10
    unidad = numero % 10

    texto = _DECENAS[
        decena
    ]

    if unidad:

        texto = (
            f"{texto} Y "
            f"{_UNIDADES[unidad]}"
        )

    return texto


def _letras_hasta_999(
    numero: int,
) -> str:

    if numero == 0:

        return ""

    if numero == 100:

        return "CIEN"

    centena = numero // 100
    resto = numero % 100

    partes: list[str] = []

    if centena:

        partes.append(
            _CENTENAS[
                centena
            ],
        )

    if resto:

        partes.append(
            _letras_hasta_99(
                resto,
            ),
        )

    return " ".join(
        partes,
    ).strip()


def _letras_entero(
    numero: int,
) -> str:

    if numero == 0:

        return "CERO"

    millones = numero // 1_000_000
    resto_millones = numero % 1_000_000
    miles = resto_millones // 1_000
    resto = resto_millones % 1_000

    partes: list[str] = []

    if millones:

        if millones == 1:

            partes.append(
                "UN MILLÓN",
            )

        else:

            partes.append(
                f"{_letras_hasta_999(millones)} MILLONES",
            )

    if miles:

        if miles == 1:

            partes.append(
                "MIL",
            )

        else:

            partes.append(
                f"{_letras_hasta_999(miles)} MIL",
            )

    if resto:

        partes.append(
            _letras_hasta_999(
                resto,
            ),
        )

    return " ".join(
        partes,
    ).strip()


def numero_a_letras(
    valor: float,
    *,
    moneda: str = "PESOS",
) -> str:

    entero = int(
        round(
            float(
                valor or 0,
            ),
        ),
    )

    texto = _letras_entero(
        abs(
            entero,
        ),
    )

    if entero < 0:

        texto = f"MENOS {texto}"

    return f"{texto} {moneda} M/CTE"
