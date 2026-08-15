from __future__ import annotations

from .constantes import (
    AUXILIO_TRANSPORTE,
    DIAS_ANIO,
    DIAS_SEMESTRE,
    DIAS_VACACIONES_ANIO,
    SMMLV,
)


def _redondear(valor: float) -> float:

    return round(
        float(valor or 0),
        0,
    )


def calcular_base_prestacional(
    salario: float,
    *,
    auxilio_transporte: float = 0,
    salario_integral: bool = False,
    promedio_devengos: float = 0,
) -> float:

    if salario <= 0:

        raise ValueError(
            "El salario debe ser mayor a cero.",
        )

    base = float(
        promedio_devengos or salario,
    )

    if salario_integral:

        return _redondear(
            base * 0.7,
        )

    auxilio = float(
        auxilio_transporte or 0,
    )

    if auxilio <= 0 and salario <= 2 * SMMLV:

        auxilio = float(
            AUXILIO_TRANSPORTE,
        )

    if salario > 2 * SMMLV:

        auxilio = 0

    return _redondear(
        base + auxilio,
    )


def calcular_provision_mensual(
    base: float,
    *,
    dias_trabajados: int = 30,
    dias_mes: int = 30,
) -> dict[str, float]:
    """
    Provisión mensual: prima, cesantías, vacaciones e intereses de cesantías.
    """

    if base <= 0:

        raise ValueError(
            "La base prestacional debe ser mayor a cero.",
        )

    factor = max(
        min(
            float(dias_trabajados)
            / float(dias_mes or 30),
            1,
        ),
        0,
    )

    base_periodo = _redondear(
        base * factor,
    )

    prima = _redondear(
        base_periodo / 12,
    )

    cesantias = _redondear(
        base_periodo / 12,
    )

    vacaciones = _redondear(
        base_periodo
        * DIAS_VACACIONES_ANIO
        / DIAS_ANIO,
    )

    intereses_cesantias = _redondear(
        cesantias * 0.01,
    )

    return {
        "prima": prima,
        "cesantias": cesantias,
        "vacaciones": vacaciones,
        "intereses_cesantias": intereses_cesantias,
    }


def calcular_prima_semestral(
    base: float,
    *,
    dias_trabajados_semestre: int,
) -> float:

    return _redondear(
        base
        * dias_trabajados_semestre
        / DIAS_SEMESTRE,
    )


def calcular_liquidacion_cesantias(
    base: float,
    *,
    dias_trabajados: int,
) -> float:

    return _redondear(
        base
        * dias_trabajados
        / DIAS_ANIO,
    )


def calcular_liquidacion_vacaciones(
    base: float,
    *,
    dias_pendientes: float = DIAS_VACACIONES_ANIO,
) -> float:

    return _redondear(
        base
        * dias_pendientes
        / DIAS_ANIO,
    )


def calcular_intereses_cesantias(
    saldo_cesantias: float,
    *,
    dias: int = 30,
) -> float:

    return _redondear(
        saldo_cesantias
        * 0.12
        * dias
        / DIAS_ANIO,
    )


def total_provision(
    provisiones: dict[str, float],
) -> float:

    return sum(
        float(valor or 0)
        for valor in provisiones.values()
    )
