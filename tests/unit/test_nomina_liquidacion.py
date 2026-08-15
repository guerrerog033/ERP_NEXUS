from aplicacion.modulos.nomina.motor_liquidacion import (
    liquidar_salario,
    totales_liquidacion,
)


def test_liquidacion_salario_basico():

    conceptos = liquidar_salario(
        salario_basico=2_000_000,
        dias_trabajados=30,
    )

    totales = totales_liquidacion(
        conceptos,
    )

    assert totales["devengado"] == 2_000_000
    assert totales["deducciones"] > 0
    assert totales["neto"] < totales["devengado"]
    assert totales["aportes_patronales"] > totales["deducciones"]


def test_liquidacion_proporcional():

    conceptos = liquidar_salario(
        salario_basico=3_000_000,
        dias_trabajados=15,
    )

    totales = totales_liquidacion(
        conceptos,
    )

    assert totales["devengado"] == 1_500_000
