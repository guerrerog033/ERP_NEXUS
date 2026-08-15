from __future__ import annotations

import hashlib
import platform
import uuid


def obtener_huella_equipo() -> str:

    partes = [
        platform.node(),
        platform.system(),
        platform.machine(),
        str(
            uuid.getnode(),
        ),
    ]

    texto = "|".join(
        partes,
    )

    return hashlib.sha256(
        texto.encode(
            "utf-8",
        ),
    ).hexdigest()
