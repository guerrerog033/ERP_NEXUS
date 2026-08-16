from __future__ import annotations

from aplicacion.maestros.productos.importacion_excel import (
    COLUMNAS,
    _fila_a_datos,
    _fila_vacia,
    _valor_celda,
)


def test_valor_celda_numerico_convierte_a_float():

    assert _valor_celda("50000", "precio_venta") == 50000.0
    assert _valor_celda(None, "costo") == 0
    assert _valor_celda("no-es-numero", "stock_minimo") == 0


def test_valor_celda_texto_recorta_espacios():

    assert _valor_celda("  Bebidas  ", "categoria") == "Bebidas"
    assert _valor_celda(None, "categoria") == ""


def test_fila_vacia_detecta_fila_sin_datos():

    assert _fila_vacia((None, "", None)) is True
    assert _fila_vacia((None, "PRD-1", None)) is False


def test_fila_a_datos_mapea_por_posicion_de_columna():

    fila = tuple("valor" for _ in COLUMNAS)

    datos = _fila_a_datos(fila)

    assert set(datos.keys()) == {
        campo for campo, _ in COLUMNAS
    }

    assert datos["codigo"] == "valor"
