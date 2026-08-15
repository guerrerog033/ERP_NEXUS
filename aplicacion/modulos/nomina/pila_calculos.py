from __future__ import annotations

from .constantes import (
    SMMLV,
    TOPE_IBC_SMMLV,
)
from .constantes import (
    TASA_CAJA_COMPENSACION,
    TASA_ICBF,
    TASA_PENSION_EMPLEADOR,
    TASA_SALUD_EMPLEADOR,
    TASA_SENA,
)


def calcular_ibc_legal(
    devengado: float,
    *,
    salario_basico: float | None = None,
) -> float:

    referencia = float(
        salario_basico
        if salario_basico is not None
        else devengado
        or 0,
    )

    ibc = float(
        devengado or 0,
    )

    minimo = float(
        SMMLV,
    )

    maximo = float(
        SMMLV * TOPE_IBC_SMMLV,
    )

    if ibc < minimo:

        ibc = minimo

    if referencia >= minimo and ibc > maximo:

        ibc = maximo

    return round(
        ibc,
        0,
    )


def calcular_arl(
    ibc: float,
    *,
    clase_riesgo: str = "1",
) -> float:

    from .constantes import (
        TARIFAS_ARL,
    )

    tarifa = TARIFAS_ARL.get(
        str(clase_riesgo or "1"),
        TARIFAS_ARL["1"],
    )

    return round(
        float(ibc or 0) * tarifa,
        0,
    )


def descomponer_aportes_pila(
    *,
    ibc: float,
    salario_basico: float,
    fsp: float = 0,
) -> dict[str, float | str]:

    salud_empleado = round(
        ibc * 0.04,
        0,
    )

    pension_empleado = round(
        ibc * 0.04,
        0,
    )

    salud_patronal = round(
        ibc * TASA_SALUD_EMPLEADOR,
        0,
    )

    pension_patronal = round(
        ibc * TASA_PENSION_EMPLEADOR,
        0,
    )

    caja = round(
        ibc * TASA_CAJA_COMPENSACION,
        0,
    )

    sena = round(
        ibc * TASA_SENA,
        0,
    )

    icbf = round(
        ibc * TASA_ICBF,
        0,
    )

    return {
        "salario_basico": salario_basico,
        "ibc": ibc,
        "salud_empleado": salud_empleado,
        "pension_empleado": pension_empleado,
        "salud_patronal": salud_patronal,
        "pension_patronal": pension_patronal,
        "fsp": fsp,
        "caja": caja,
        "sena": sena,
        "icbf": icbf,
        "tarifa_pension": "0120000",
        "tarifa_salud": "0085000",
        "tarifa_caja": "0040000",
        "tarifa_sena": "0020000",
        "tarifa_icbf": "0030000",
    }
