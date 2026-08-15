from aplicacion.modulos.nomina.exportadores.pila_aportes import (
    ExportadorPilaAportesEnLinea,
)
from aplicacion.modulos.nomina.exportadores.pila_formato import (
    REGISTRO_02_LONGITUD,
    campo_numerico,
    tarifa_pila,
)
from aplicacion.modulos.nomina.motor_liquidacion import (
    liquidar_con_arl,
)
from aplicacion.modulos.nomina.motor_prestaciones import (
    calcular_base_prestacional,
    calcular_intereses_cesantias,
    calcular_prima_semestral,
)
from aplicacion.modulos.nomina.constantes import (
    SMMLV,
    TOPE_IBC_SMMLV,
)
from aplicacion.modulos.nomina.pila_calculos import (
    calcular_ibc_legal,
)


def test_pila_formato_tarifa():

    assert tarifa_pila(0.12) == "0120000"
    assert tarifa_pila(0.085) == "0085000"


def test_pila_registro_longitud(tmp_path, monkeypatch):

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
                else (
                    "1"
                    if args[:2] == ("empresa", "dv")
                    else "Empresa Demo"
                )
            )
        ),
    )

    rutas = ExportadorPilaAportesEnLinea.generar(
        anio=2026,
        mes=8,
        aportante={
            "nit": "900123456",
            "razon_social": "Empresa Demo",
            "dv": "1",
        },
        liquidaciones=[
            {
                "tipo_documento": "CC",
                "numero_documento": "123456789",
                "tipo_cotizante": "01",
                "subtipo_cotizante": "00",
                "departamento": "11",
                "municipio": "001",
                "primer_apellido": "PEREZ",
                "segundo_apellido": "",
                "primer_nombre": "JUAN",
                "segundo_nombre": "",
                "dias_cotizados": 30,
                "salario_basico": 2_000_000,
                "ibc": 2_000_000,
                "eps_codigo": "EPS037",
                "afp_codigo": "230201",
                "arl_codigo": "140099",
                "ccf_codigo": "CCF001",
                "clase_riesgo": "1",
                "centro_trabajo": "000000001",
                "tarifa_arl": 0.00522,
                "pension_patronal": 240_000,
                "salud_patronal": 170_000,
                "fsp": 0,
                "arl_valor": 10_440,
                "caja": 80_000,
                "sena": 40_000,
                "icbf": 60_000,
            },
        ],
    )

    contenido = open(
        rutas["tipo2"],
        encoding="utf-8",
    ).read()

    lineas = contenido.splitlines()

    assert len(lineas) == 2
    assert lineas[0].startswith("01")
    assert lineas[1].startswith("02")
    assert len(lineas[1]) == REGISTRO_02_LONGITUD


def test_ibc_legal_tope():

    ibc = calcular_ibc_legal(
        100_000_000,
        salario_basico=2_000_000,
    )

    assert ibc == SMMLV * TOPE_IBC_SMMLV


def test_liquidacion_incluye_arl():

    conceptos = liquidar_con_arl(
        salario_basico=2_000_000,
        dias_trabajados=30,
        clase_riesgo="1",
    )

    codigos = {
        item.codigo
        for item in conceptos
    }

    assert "206" in codigos


def test_prestaciones_base_integral():

    base = calcular_base_prestacional(
        salario=10_000_000,
        salario_integral=True,
    )

    assert base == 7_000_000


def test_prestaciones_intereses_cesantias():

    intereses = calcular_intereses_cesantias(
        1_000_000,
        dias=30,
    )

    assert intereses == 10_000


def test_prima_semestral():

    valor = calcular_prima_semestral(
        3_000_000,
        dias_trabajados_semestre=180,
    )

    assert valor == 3_000_000


def test_campo_numerico_padding():

    assert campo_numerico(
        42,
        5,
    ) == "00042"
