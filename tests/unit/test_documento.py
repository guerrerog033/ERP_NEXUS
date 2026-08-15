from aplicacion.dominio.documentos.dv import DVCalculator
from aplicacion.dominio.documentos.resultado import DocumentoResult

def test_dv_nit_conocido():
    dv = DVCalculator.calcular("900123456")
    assert isinstance(dv, str)
    assert len(dv) == 1


def test_documento_result_compatibilidad():
    resultado = DocumentoResult(
        tipo="NIT",
        numero="900123456",
        dv="1",
        razon_social="Prueba SAS",
    )

    assert resultado.tipo_documento == "NIT"
    assert resultado.numero_documento == "900123456"
    assert resultado.encontrado is True


def test_documento_result_vacio():
    resultado = DocumentoResult()

    assert resultado.encontrado is False
    assert resultado.ok is False
