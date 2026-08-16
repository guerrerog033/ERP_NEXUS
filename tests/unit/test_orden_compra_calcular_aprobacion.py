from __future__ import annotations

from aplicacion.modulos.compras.ordenes.servicios import (
    ServicioOrdenCompra,
)
from aplicacion.nucleo.configuracion import Configuracion


def _configurar(monkeypatch, nivel1=0, nivel2=0):

    datos = Configuracion.cargar()

    monkeypatch.setitem(
        datos,
        "compras",
        {
            "aprobacion_nivel1_monto": nivel1,
            "aprobacion_nivel2_monto": nivel2,
        },
    )


def test_sin_umbral_configurado_no_requiere_aprobacion(
    monkeypatch,
):

    _configurar(monkeypatch, nivel1=0)

    assert (
        ServicioOrdenCompra._calcular_estado_aprobacion(
            1000000,
        )
        == "no_aplica"
    )


def test_bajo_el_umbral_no_requiere_aprobacion(
    monkeypatch,
):

    _configurar(monkeypatch, nivel1=5000)

    assert (
        ServicioOrdenCompra._calcular_estado_aprobacion(
            4999,
        )
        == "no_aplica"
    )


def test_en_o_sobre_el_umbral_requiere_aprobacion(
    monkeypatch,
):

    _configurar(monkeypatch, nivel1=5000)

    assert (
        ServicioOrdenCompra._calcular_estado_aprobacion(
            5000,
        )
        == "pendiente_nivel1"
    )

    assert (
        ServicioOrdenCompra._calcular_estado_aprobacion(
            10000,
        )
        == "pendiente_nivel1"
    )
