from __future__ import annotations

from datetime import date

import pytest

from aplicacion.modulos.ventas.facturacion_recurrente.utilidades import (
    calcular_proxima_fecha,
    sumar_meses,
)


def test_sumar_meses_caso_simple():

    assert sumar_meses(date(2026, 1, 15), 1) == date(2026, 2, 15)


def test_sumar_meses_cruza_fin_de_anio():

    assert sumar_meses(date(2026, 12, 5), 1) == date(2027, 1, 5)


def test_sumar_meses_ajusta_dia_inexistente():

    assert sumar_meses(date(2026, 1, 31), 1) == date(2026, 2, 28)


def test_sumar_meses_respeta_anio_bisiesto():

    assert sumar_meses(date(2028, 1, 31), 1) == date(2028, 2, 29)


def test_sumar_meses_varios_meses():

    assert sumar_meses(date(2026, 1, 31), 3) == date(2026, 4, 30)


def test_calcular_proxima_fecha_quincenal():

    assert calcular_proxima_fecha(
        date(2026, 1, 1),
        "quincenal",
    ) == date(2026, 1, 16)


def test_calcular_proxima_fecha_mensual():

    assert calcular_proxima_fecha(
        date(2026, 1, 31),
        "mensual",
    ) == date(2026, 2, 28)


def test_calcular_proxima_fecha_trimestral():

    assert calcular_proxima_fecha(
        date(2026, 1, 31),
        "trimestral",
    ) == date(2026, 4, 30)


def test_calcular_proxima_fecha_anual():

    assert calcular_proxima_fecha(
        date(2028, 2, 29),
        "anual",
    ) == date(2029, 2, 28)


def test_calcular_proxima_fecha_periodicidad_desconocida():

    with pytest.raises(ValueError):

        calcular_proxima_fecha(date(2026, 1, 1), "semanal")
