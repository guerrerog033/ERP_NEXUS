from __future__ import annotations

import hashlib
import hmac
import re
import secrets

from aplicacion.licencias.ediciones import (
    CODIGO_A_EDICION,
    EDICIONES,
)

_ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

_PREFIJO = "NEXUS"

_LONGITUD_PAQUETE = 11

_LONGITUD_CODIFICADO = 20

_SERIAL_RE = re.compile(
    r"^NEXUS(?:-[A-Z0-9]{4}){5}$",
)


def _codificar_paquete(
    datos: bytes,
) -> str:

    if len(datos) != _LONGITUD_PAQUETE:

        raise ValueError(
            "Paquete de serial inválido.",
        )

    valor = int.from_bytes(
        datos,
        "big",
    )

    codificado = ""

    for _ in range(
        _LONGITUD_CODIFICADO,
    ):

        valor, resto = divmod(
            valor,
            len(_ALFABETO),
        )

        codificado = (
            _ALFABETO[resto]
            + codificado
        )

    return codificado


def _decodificar_paquete(
    codificado: str,
) -> bytes:

    if len(codificado) != _LONGITUD_CODIFICADO:

        raise ValueError(
            "Serial corrupto.",
        )

    valor = 0

    for caracter in codificado:

        indice = _ALFABETO.find(
            caracter,
        )

        if indice < 0:

            raise ValueError(
                "Serial inválido.",
            )

        valor = (
            valor * len(_ALFABETO)
            + indice
        )

    return valor.to_bytes(
        _LONGITUD_PAQUETE,
        "big",
    )


def normalizar_serial(
    serial: str,
) -> str:

    limpio = (
        serial or ""
    ).strip().upper()

    limpio = limpio.replace(
        " ",
        "",
    )

    return limpio


def generar_serial(
    edicion: str,
    *,
    dias: int | None = None,
    secreto: str,
) -> str:

    if edicion not in EDICIONES:

        raise ValueError(
            f"Edición desconocida: {edicion}",
        )

    datos_edicion = EDICIONES[
        edicion
    ]

    codigo = datos_edicion[
        "codigo_serial"
    ]

    if dias is None:

        dias = datos_edicion.get(
            "dias_predeterminados",
        )

    if dias is None:

        dias = 0

    if (
        dias < 0
        or dias > 65535
    ):

        raise ValueError(
            "Los días de validez deben estar entre 0 y 65535.",
        )

    aleatorio = secrets.token_bytes(
        4,
    )

    cuerpo = (
        b"\x01"
        + codigo.encode(
            "ascii",
        )
        + aleatorio
        + dias.to_bytes(
            2,
            "big",
        )
    )

    firma = hmac.new(
        secreto.encode(
            "utf-8",
        ),
        cuerpo,
        hashlib.sha256,
    ).digest()[
        :2
    ]

    paquete = cuerpo + firma

    codificado = _codificar_paquete(
        paquete,
    )

    grupos = [
        codificado[
            indice: indice + 4
        ]
        for indice in range(
            0,
            _LONGITUD_CODIFICADO,
            4,
        )
    ]

    return (
        f"{_PREFIJO}-"
        + "-".join(
            grupos,
        )
    )


def decodificar_serial(
    serial: str,
    *,
    secreto: str,
) -> dict:

    normalizado = normalizar_serial(
        serial,
    )

    if not _SERIAL_RE.match(
        normalizado,
    ):

        raise ValueError(
            "Formato de serial inválido.",
        )

    cuerpo = normalizado[
        len(_PREFIJO) + 1:
    ].replace(
        "-",
        "",
    )

    paquete = _decodificar_paquete(
        cuerpo,
    )

    if len(paquete) != _LONGITUD_PAQUETE:

        raise ValueError(
            "Serial corrupto.",
        )

    version = paquete[0]

    if version != 1:

        raise ValueError(
            "Versión de serial no soportada.",
        )

    codigo_edicion = paquete[
        1:3
    ].decode(
        "ascii",
        errors="ignore",
    )

    edicion = CODIGO_A_EDICION.get(
        codigo_edicion,
    )

    if edicion is None:

        raise ValueError(
            "Edición del serial desconocida.",
        )

    dias = int.from_bytes(
        paquete[7:9],
        "big",
    )

    firma_esperada = paquete[9:11]

    cuerpo_firmado = paquete[:9]

    firma_calculada = hmac.new(
        secreto.encode(
            "utf-8",
        ),
        cuerpo_firmado,
        hashlib.sha256,
    ).digest()[
        :2
    ]

    if not hmac.compare_digest(
        firma_esperada,
        firma_calculada,
    ):

        raise ValueError(
            "Serial no válido o alterado.",
        )

    return {

        "edicion": edicion,

        "dias_validez": (
            None
            if dias == 0
            else dias
        ),

        "modulos": list(
            EDICIONES[edicion][
                "modulos"
            ],
        ),

        "max_usuarios": int(
            EDICIONES[edicion][
                "max_usuarios"
            ],
        ),

    }
