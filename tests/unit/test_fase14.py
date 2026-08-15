from aplicacion.dominio.credito.cupo import evaluar_cupo
from aplicacion.dominio.documentos.consulta import (
    consultar,
    registrar,
)
from aplicacion.dominio.documentos.dv import DVCalculator
from aplicacion.dominio.documentos.normalizador import NormalizadorDocumento
from aplicacion.dominio.documentos.resultado import DocumentoResult
from aplicacion.dominio.documentos.servicio import ServicioDocumento
from aplicacion.dominio.documentos.validador import ValidadorDocumento
from aplicacion.dominio.impuestos.linea import calcular_linea
from aplicacion.dominio.impuestos.totales import calcular_totales_lineas


def test_preparar_nit_calcula_dv():
    numero, dv = ServicioDocumento.preparar(
        "NIT",
        "900123456",
    )

    assert numero == "900123456"
    assert dv == DVCalculator.calcular(
        "900123456",
    )


def test_fusionar_completa_campos():
    destino = DocumentoResult(
        tipo="NIT",
        numero="900",
    )

    origen = DocumentoResult(
        razon_social="ACME SAS",
        origen="DIAN",
    )

    ServicioDocumento.fusionar(
        destino,
        origen,
    )

    assert destino.razon_social == "ACME SAS"
    assert destino.origen == "DIAN"


def test_consulta_sin_procesador():
    from aplicacion.dominio.documentos import consulta as modulo_consulta

    procesador_previo = modulo_consulta.obtener_procesador()
    modulo_consulta._procesador = None

    try:
        resultado = consultar(
            "CC",
            "123",
        )

        assert "procesador" in resultado.mensaje.lower()
    finally:
        modulo_consulta._procesador = procesador_previo


def test_consulta_con_procesador_registrado():
    from aplicacion.dominio.documentos import consulta as modulo_consulta

    procesador_previo = modulo_consulta.obtener_procesador()

    def _fake(
        tipo,
        numero,
    ):
        return DocumentoResult(
            tipo=str(
                tipo,
            ),
            numero=str(
                numero,
            ),
            razon_social="Prueba",
        )

    registrar(
        _fake,
    )

    try:
        resultado = consultar(
            "NIT",
            "1",
        )

        assert resultado.encontrado is True
        assert resultado.razon_social == "Prueba"
    finally:
        modulo_consulta._procesador = procesador_previo


def test_calcular_linea_con_iva():
    subtotal, total = calcular_linea(
        2,
        100,
        19,
    )

    assert subtotal == 200.0
    assert total == 238.0


def test_calcular_linea_precio_incluye_iva():
    subtotal, total = calcular_linea(
        1,
        119,
        19,
        precio_incluye_iva=True,
    )

    assert subtotal == 100.0
    assert total == 119.0


def test_calcular_totales_lineas():
    lineas = [
        {
            "cantidad": 2,
            "precio_unitario": 50,
            "porcentaje_impuesto": 19,
        },
    ]

    subtotal, iva, total = calcular_totales_lineas(
        lineas,
    )

    assert subtotal == 100.0
    assert iva == 19.0
    assert total == 119.0
    assert lineas[0]["total_linea"] == 119.0


def test_evaluar_cupo_permitido():
    resultado = evaluar_cupo(
        1_000_000,
        200_000,
        300_000,
    )

    assert resultado.permitido is True
    assert resultado.disponible == 800_000


def test_evaluar_cupo_excedido():
    resultado = evaluar_cupo(
        500_000,
        400_000,
        200_000,
    )

    assert resultado.permitido is False
    assert "excedido" in resultado.mensaje.lower()


def test_normalizador_y_validador():
    assert NormalizadorDocumento.normalizar(
        " 900-123.456 ",
    ) == "900123456"

    try:
        ValidadorDocumento.validar(
            "CC",
            "",
        )
        raise AssertionError(
            "Debía fallar con documento vacío",
        )
    except ValueError:
        pass


def test_documento_result_en_dominio():
    resultado = DocumentoResult(
        tipo="NIT",
        numero="900123456",
        dv="1",
        razon_social="Prueba SAS",
    )

    assert resultado.tipo_documento == "NIT"
    assert resultado.encontrado is True
