from __future__ import annotations

import pytest

from aplicacion.maestros.productos.precio_volumen_servicio import (
    ServicioPrecioVolumenProducto,
)


def test_validar_requiere_producto_id():

    with pytest.raises(ValueError, match="producto"):

        ServicioPrecioVolumenProducto._validar(
            {
                "cantidad_minima": "10",
                "precio": "1000",
            },
        )


def test_validar_requiere_cantidad_minima_positiva():

    with pytest.raises(ValueError, match="cantidad mínima"):

        ServicioPrecioVolumenProducto._validar(
            {
                "producto_id": 1,
                "cantidad_minima": "0",
                "precio": "1000",
            },
        )


def test_validar_requiere_precio_positivo():

    with pytest.raises(ValueError, match="precio"):

        ServicioPrecioVolumenProducto._validar(
            {
                "producto_id": 1,
                "cantidad_minima": "10",
                "precio": "0",
            },
        )


def test_validar_convierte_valores_de_texto_a_numero():

    datos = {
        "producto_id": 1,
        "cantidad_minima": "10",
        "precio": "9000",
    }

    ServicioPrecioVolumenProducto._validar(datos)

    assert datos["cantidad_minima"] == 10.0
    assert datos["precio"] == 9000.0
