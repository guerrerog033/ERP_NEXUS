from aplicacion.modulos.nomina.motor_liquidacion import (
    NovedadLiquidacion,
    liquidar_salario,
    totales_liquidacion,
)
from aplicacion.modulos.nomina.motor_prestaciones import (
    calcular_base_prestacional,
    calcular_provision_mensual,
    total_provision,
)
from aplicacion.modulos.nomina.exportadores.pila import (
    ExportadorPila,
)


def test_liquidacion_con_horas_extra():

    conceptos = liquidar_salario(
        salario_basico=2_000_000,
        dias_trabajados=30,
        novedades=[
            NovedadLiquidacion(
                tipo="hora_extra",
                cantidad=8,
            ),
        ],
    )

    totales = totales_liquidacion(
        conceptos,
    )

    assert totales["devengado"] > 2_000_000


def test_liquidacion_con_incapacidad():

    conceptos = liquidar_salario(
        salario_basico=3_000_000,
        dias_trabajados=30,
        novedades=[
            NovedadLiquidacion(
                tipo="incapacidad",
                cantidad=5,
            ),
        ],
    )

    totales = totales_liquidacion(
        conceptos,
    )

    assert totales["devengado"] < 3_000_000


def test_provision_prestaciones():

    base = calcular_base_prestacional(
        3_000_000,
        auxilio_transporte=200_000,
    )

    provisiones = calcular_provision_mensual(
        base,
    )

    assert provisiones["prima"] > 0
    assert provisiones["intereses_cesantias"] > 0
    assert total_provision(provisiones) > provisiones["vacaciones"]


def test_exportador_pila(tmp_path, monkeypatch):

    from aplicacion.nucleo import configuracion

    monkeypatch.setattr(
        configuracion.Configuracion,
        "obtener",
        lambda *args, **kwargs: (
            str(tmp_path)
            if args[:2] == ("nomina", "ruta_pila")
            else (
                "900123456"
                if args[:2] == ("empresa", "nit")
                else None
            )
        ),
    )

    ruta = ExportadorPila.generar(
        anio=2026,
        mes=8,
        liquidaciones=[
            {
                "tipo_documento": "CC",
                "numero_documento": "123",
                "ibc": 2_000_000,
                "salud_empleado": 80_000,
                "pension_empleado": 80_000,
                "salud_patronal": 170_000,
                "pension_patronal": 240_000,
                "fsp": 0,
            },
        ],
    )

    assert ruta.endswith(".txt")
