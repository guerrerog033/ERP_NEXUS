from __future__ import annotations

import os
import uuid

import pytest

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)


pytestmark = pytest.mark.integration


@pytest.fixture(
    scope="session",
    autouse=True,
)
def _registrar_modelos():

    importar_modelos()


@pytest.fixture(
    scope="session",
)
def requiere_postgresql():

    if not os.getenv(
        "DB_HOST",
    ):

        pytest.skip(
            "DB_HOST no configurado",
        )


@pytest.fixture
def prefijo_unico():

    return f"T{uuid.uuid4().hex[:5].upper()}"


def test_siguiente_numero_es_secuencial(
    requiere_postgresql,
    prefijo_unico,
):
    from aplicacion.nucleo.numeracion.servicio import (
        ServicioNumeracion,
    )

    numero_1 = ServicioNumeracion.siguiente_numero(
        "test_secuencial",
        prefijo_unico,
    )
    numero_2 = ServicioNumeracion.siguiente_numero(
        "test_secuencial",
        prefijo_unico,
    )
    numero_3 = ServicioNumeracion.siguiente_numero(
        "test_secuencial",
        prefijo_unico,
    )

    assert numero_1 == f"{prefijo_unico}000001"
    assert numero_2 == f"{prefijo_unico}000002"
    assert numero_3 == f"{prefijo_unico}000003"


def test_siguiente_numero_respeta_longitud_configurada(
    requiere_postgresql,
    prefijo_unico,
):
    from aplicacion.nucleo.numeracion.servicio import (
        ServicioNumeracion,
    )

    numero = ServicioNumeracion.siguiente_numero(
        "test_longitud",
        prefijo_unico,
        longitud=4,
    )

    assert numero == f"{prefijo_unico}0001"


def test_siguiente_numero_falla_al_agotar_rango(
    requiere_postgresql,
    prefijo_unico,
):
    from aplicacion.nucleo.numeracion.servicio import (
        ServicioNumeracion,
    )

    ServicioNumeracion.siguiente_numero(
        "test_rango",
        prefijo_unico,
        rango_hasta=2,
    )
    ServicioNumeracion.siguiente_numero(
        "test_rango",
        prefijo_unico,
        rango_hasta=2,
    )

    with pytest.raises(
        ValueError,
        match="rango autorizado",
    ):

        ServicioNumeracion.siguiente_numero(
            "test_rango",
            prefijo_unico,
            rango_hasta=2,
        )


def test_siguiente_numero_falla_si_vencida(
    requiere_postgresql,
    prefijo_unico,
):
    from datetime import date, timedelta

    from aplicacion.nucleo.numeracion.servicio import (
        ServicioNumeracion,
    )

    ayer = date.today() - timedelta(days=1)

    with pytest.raises(
        ValueError,
        match="venció",
    ):

        ServicioNumeracion.siguiente_numero(
            "test_vencida",
            prefijo_unico,
            fecha_fin=ayer,
        )


def test_codigo_tipo_distinto_no_comparte_secuencia(
    requiere_postgresql,
    prefijo_unico,
):
    from aplicacion.nucleo.numeracion.servicio import (
        ServicioNumeracion,
    )

    numero_a = ServicioNumeracion.siguiente_numero(
        "tipo_a",
        prefijo_unico,
    )
    numero_b = ServicioNumeracion.siguiente_numero(
        "tipo_b",
        prefijo_unico,
    )

    assert numero_a == f"{prefijo_unico}000001"
    assert numero_b == f"{prefijo_unico}000001"
