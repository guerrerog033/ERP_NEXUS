from __future__ import annotations

from dataclasses import dataclass

from .constantes import (
    SMMLV,
    TASA_CAJA_COMPENSACION,
    TASA_ICBF,
    TASA_PENSION_EMPLEADO,
    TASA_PENSION_EMPLEADOR,
    TASA_SALUD_EMPLEADO,
    TASA_SALUD_EMPLEADOR,
    TASA_SENA,
)


@dataclass(slots=True)
class ConceptoLiquidacion:

    codigo: str
    nombre: str
    naturaleza: str
    valor: float


def _redondear(valor: float) -> float:

    return round(
        float(valor or 0),
        0,
    )


def calcular_solidaridad_pensional(
    salario: float,
    ibc: float,
) -> float:

    if salario < 4 * SMMLV:

        return 0.0

    if salario < 16 * SMMLV:

        return _redondear(
            ibc * 0.01,
        )

    if salario < 17 * SMMLV:

        return _redondear(
            ibc * 0.012,
        )

    if salario < 18 * SMMLV:

        return _redondear(
            ibc * 0.014,
        )

    if salario < 19 * SMMLV:

        return _redondear(
            ibc * 0.016,
        )

    if salario < 20 * SMMLV:

        return _redondear(
            ibc * 0.018,
        )

    return _redondear(
        ibc * 0.02,
    )


@dataclass(slots=True)
class NovedadLiquidacion:

    tipo: str
    cantidad: float = 0
    valor: float = 0


def _valor_hora_extra(
    salario_basico: float,
    horas: float,
) -> float:

    if horas <= 0:

        return 0.0

    valor_hora = salario_basico / 240

    return _redondear(
        valor_hora * 1.25 * horas,
    )


def liquidar_salario(
    *,
    salario_basico: float,
    dias_trabajados: int = 30,
    novedades: list[NovedadLiquidacion] | None = None,
) -> list[ConceptoLiquidacion]:
    """
    Liquidación mensual simplificada (devengos, deducciones y aportes patronales).
    """

    novedades = novedades or []

    if dias_trabajados <= 0:

        raise ValueError(
            "Los días trabajados deben ser mayores a cero.",
        )

    if salario_basico <= 0:

        raise ValueError(
            "El salario básico debe ser mayor a cero.",
        )

    dias_incapacidad = sum(
        float(novedad.cantidad or 0)
        for novedad in novedades
        if novedad.tipo == "incapacidad"
    )

    dias_efectivos = max(
        dias_trabajados - int(dias_incapacidad),
        0,
    )

    if dias_efectivos <= 0:

        raise ValueError(
            "No hay días efectivos de trabajo en el periodo.",
        )

    basico = _redondear(
        salario_basico
        * dias_efectivos
        / 30,
    )

    devengos_extra: list[ConceptoLiquidacion] = []
    deducciones_extra: list[ConceptoLiquidacion] = []

    for novedad in novedades:

        if novedad.tipo == "hora_extra":

            valor = float(
                novedad.valor or 0,
            )

            if valor <= 0:

                valor = _valor_hora_extra(
                    salario_basico,
                    float(
                        novedad.cantidad or 0,
                    ),
                )

            if valor > 0:

                devengos_extra.append(
                    ConceptoLiquidacion(
                        "002",
                        "Horas extra",
                        "devengo",
                        valor,
                    ),
                )

        elif novedad.tipo == "bonificacion":

            valor = float(
                novedad.valor or 0,
            )

            if valor > 0:

                devengos_extra.append(
                    ConceptoLiquidacion(
                        "003",
                        "Bonificación",
                        "devengo",
                        valor,
                    ),
                )

        elif novedad.tipo == "licencia":

            valor = float(
                novedad.valor or 0,
            )

            if valor > 0:

                deducciones_extra.append(
                    ConceptoLiquidacion(
                        "104",
                        "Licencia no remunerada",
                        "deduccion",
                        valor,
                    ),
                )

    ibc = _redondear(
        basico
        + sum(
            item.valor
            for item in devengos_extra
        ),
    )

    salud = _redondear(
        ibc * TASA_SALUD_EMPLEADO,
    )

    pension = _redondear(
        ibc * TASA_PENSION_EMPLEADO,
    )

    solidaridad = calcular_solidaridad_pensional(
        salario_basico,
        ibc,
    )

    conceptos = [
        ConceptoLiquidacion(
            "001",
            "Salario básico",
            "devengo",
            basico,
        ),
        *devengos_extra,
        ConceptoLiquidacion(
            "101",
            "Aporte salud empleado",
            "deduccion",
            salud,
        ),
        ConceptoLiquidacion(
            "102",
            "Aporte pensión empleado",
            "deduccion",
            pension,
        ),
        *deducciones_extra,
    ]

    if solidaridad > 0:

        conceptos.append(
            ConceptoLiquidacion(
                "103",
                "Fondo solidaridad pensional",
                "deduccion",
                solidaridad,
            ),
        )

    conceptos.extend(
        [
            ConceptoLiquidacion(
                "201",
                "Salud empleador",
                "aporte_patronal",
                _redondear(
                    ibc * TASA_SALUD_EMPLEADOR,
                ),
            ),
            ConceptoLiquidacion(
                "202",
                "Pensión empleador",
                "aporte_patronal",
                _redondear(
                    ibc * TASA_PENSION_EMPLEADOR,
                ),
            ),
            ConceptoLiquidacion(
                "203",
                "Caja de compensación",
                "aporte_patronal",
                _redondear(
                    ibc * TASA_CAJA_COMPENSACION,
                ),
            ),
            ConceptoLiquidacion(
                "204",
                "ICBF",
                "aporte_patronal",
                _redondear(
                    ibc * TASA_ICBF,
                ),
            ),
            ConceptoLiquidacion(
                "205",
                "SENA",
                "aporte_patronal",
                _redondear(
                    ibc * TASA_SENA,
                ),
            ),
        ],
    )

    return conceptos


def liquidar_con_arl(
    *,
    salario_basico: float,
    dias_trabajados: int = 30,
    novedades: list[NovedadLiquidacion] | None = None,
    clase_riesgo: str = "1",
) -> list[ConceptoLiquidacion]:

    conceptos = liquidar_salario(
        salario_basico=salario_basico,
        dias_trabajados=dias_trabajados,
        novedades=novedades,
    )

    from .pila_calculos import (
        calcular_arl,
        calcular_ibc_legal,
    )

    devengado = sum(
        item.valor
        for item in conceptos
        if item.naturaleza == "devengo"
    )

    ibc = calcular_ibc_legal(
        devengado,
        salario_basico=salario_basico,
    )

    arl = calcular_arl(
        ibc,
        clase_riesgo=clase_riesgo,
    )

    if arl > 0:

        conceptos.append(
            ConceptoLiquidacion(
                "206",
                "ARL",
                "aporte_patronal",
                arl,
            ),
        )

    return conceptos


def totales_liquidacion(
    conceptos: list[ConceptoLiquidacion],
) -> dict[str, float]:

    devengado = sum(
        c.valor
        for c in conceptos
        if c.naturaleza == "devengo"
    )

    deducciones = sum(
        c.valor
        for c in conceptos
        if c.naturaleza == "deduccion"
    )

    aportes = sum(
        c.valor
        for c in conceptos
        if c.naturaleza == "aporte_patronal"
    )

    return {
        "devengado": devengado,
        "deducciones": deducciones,
        "neto": devengado - deducciones,
        "aportes_patronales": aportes,
    }
