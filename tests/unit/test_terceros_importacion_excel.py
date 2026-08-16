from __future__ import annotations

from aplicacion.maestros.terceros.importacion_excel import (
    COLUMNAS,
    _fila_a_datos,
    _fila_vacia,
    _valor_celda,
)


def test_valor_celda_numerico_convierte_a_float():

    assert _valor_celda("30", "dias_credito") == 30.0
    assert _valor_celda(None, "dias_credito") == 0
    assert _valor_celda("no-es-numero", "cupo_credito") == 0


def test_valor_celda_texto_recorta_espacios():

    assert _valor_celda("  Bogotá  ", "ciudad") == "Bogotá"
    assert _valor_celda(None, "ciudad") == ""


def test_fila_vacia_detecta_fila_sin_datos():

    assert _fila_vacia((None, "", None)) is True
    assert _fila_vacia((None, "NIT", None)) is False


def test_fila_a_datos_mapea_por_posicion_de_columna():

    fila = tuple(
        "valor" for _ in COLUMNAS
    )

    datos = _fila_a_datos(fila)

    assert set(datos.keys()) == {
        campo for campo, _ in COLUMNAS
    }

    assert datos["tipo_documento"] == "valor"
