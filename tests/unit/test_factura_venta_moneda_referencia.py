from __future__ import annotations

import pytest

from aplicacion.modulos.ventas.facturas.servicios import (
    ServicioFacturaVenta,
)


def test_sin_moneda_deja_ambos_campos_en_none():

    cabecera = {"moneda_referencia": "", "tasa_cambio_referencia": 0}

    ServicioFacturaVenta._normalizar_moneda_referencia(cabecera)

    assert cabecera["moneda_referencia"] is None
    assert cabecera["tasa_cambio_referencia"] is None


def test_moneda_cop_se_trata_como_sin_referencia():

    cabecera = {
        "moneda_referencia": "cop",
        "tasa_cambio_referencia": 1,
    }

    ServicioFacturaVenta._normalizar_moneda_referencia(cabecera)

    assert cabecera["moneda_referencia"] is None
    assert cabecera["tasa_cambio_referencia"] is None


def test_moneda_extranjera_sin_tasa_falla():

    cabecera = {
        "moneda_referencia": "USD",
        "tasa_cambio_referencia": 0,
    }

    with pytest.raises(ValueError, match="tasa de cambio"):

        ServicioFacturaVenta._normalizar_moneda_referencia(
            cabecera,
        )


def test_moneda_extranjera_normaliza_mayusculas_y_tasa():

    cabecera = {
        "moneda_referencia": "usd",
        "tasa_cambio_referencia": "4150.5",
    }

    ServicioFacturaVenta._normalizar_moneda_referencia(cabecera)

    assert cabecera["moneda_referencia"] == "USD"
    assert cabecera["tasa_cambio_referencia"] == 4150.5
