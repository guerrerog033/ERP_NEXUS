from __future__ import annotations

import hashlib
from datetime import date, datetime


def _formato_decimal(
    valor: float,
    decimales: int = 2,
) -> str:

    return f"{float(valor):.{decimales}f}"


def calcular_cufe(
    *,
    numero: str,
    fecha: date,
    hora: datetime | None = None,
    valor_factura: float,
    valor_iva: float,
    valor_otros_impuestos: float = 0.0,
    valor_total: float,
    nit_emisor: str,
    nit_adquiriente: str,
    clave_tecnica: str,
    ambiente: str = "2",
) -> str:

    if hora is None:

        hora = datetime.now()

    fec = fecha.strftime("%Y-%m-%d")
    hor = hora.strftime("%H:%M:%S-05:00")

    cadena = "^".join(
        [
            str(numero),
            fec,
            hor,
            _formato_decimal(valor_factura),
            "01",
            _formato_decimal(valor_iva),
            "04",
            _formato_decimal(valor_otros_impuestos),
            "03",
            "0.00",
            _formato_decimal(valor_total),
            str(nit_emisor).replace(
                "-",
                "",
            ),
            str(nit_adquiriente).replace(
                "-",
                "",
            ),
            str(clave_tecnica),
            str(ambiente),
        ],
    )

    digest = hashlib.sha384(
        cadena.encode("utf-8"),
    ).hexdigest()

    return digest
