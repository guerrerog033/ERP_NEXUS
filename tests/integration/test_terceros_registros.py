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
def tercero_id(
    requiere_postgresql,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    sufijo = uuid.uuid4().hex[:8]

    documento = str(
        900000000
        + int(sufijo[:6], 16) % 100000000,
    )

    tercero = TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": documento,
            "tipo_tercero": "Cliente",
            "razon_social": f"Tercero Registros Demo {sufijo}",
            "direccion": "Calle 1 # 2-3",
            "pais": "Colombia",
            "departamento": "Cundinamarca",
            "ciudad": "Bogotá",
            "correo": f"registros.{sufijo}@demo.com",
            "dias_credito": 0,
            "cupo_credito": 0,
            "resp_r99_pn": True,
        },
    )

    return tercero.id


def test_cuenta_bancaria_guardar_y_listar(
    tercero_id,
):
    from aplicacion.maestros.terceros.servicio_registros import (
        ServicioCuentaBancariaTercero,
    )

    ServicioCuentaBancariaTercero.guardar(
        {
            "tercero_id": tercero_id,
            "banco": "Bancolombia",
            "tipo_cuenta": "Ahorros",
            "numero_cuenta": "12345678901",
        },
    )

    cuentas = ServicioCuentaBancariaTercero.listar(
        tercero_id,
    )

    assert len(cuentas) == 1
    assert cuentas[0].banco == "Bancolombia"


def test_cuenta_bancaria_exige_campos_obligatorios(
    tercero_id,
):
    from aplicacion.maestros.terceros.servicio_registros import (
        ServicioCuentaBancariaTercero,
    )

    with pytest.raises(
        ValueError,
        match="banco",
    ):

        ServicioCuentaBancariaTercero.guardar(
            {
                "tercero_id": tercero_id,
                "numero_cuenta": "123",
            },
        )


def test_solo_una_cuenta_principal_por_tercero(
    tercero_id,
):
    from aplicacion.maestros.terceros.servicio_registros import (
        ServicioCuentaBancariaTercero,
    )

    primera = ServicioCuentaBancariaTercero.guardar(
        {
            "tercero_id": tercero_id,
            "banco": "Bancolombia",
            "numero_cuenta": "111",
            "principal": True,
        },
    )

    segunda = ServicioCuentaBancariaTercero.guardar(
        {
            "tercero_id": tercero_id,
            "banco": "Davivienda",
            "numero_cuenta": "222",
            "principal": True,
        },
    )

    cuentas = {
        cuenta.id: cuenta.principal
        for cuenta in ServicioCuentaBancariaTercero.listar(
            tercero_id,
        )
    }

    assert cuentas[primera.id] is False
    assert cuentas[segunda.id] is True


def test_cuenta_bancaria_eliminar(
    tercero_id,
):
    from aplicacion.maestros.terceros.servicio_registros import (
        ServicioCuentaBancariaTercero,
    )

    cuenta = ServicioCuentaBancariaTercero.guardar(
        {
            "tercero_id": tercero_id,
            "banco": "Bancolombia",
            "numero_cuenta": "999",
        },
    )

    ServicioCuentaBancariaTercero.eliminar(
        cuenta.id,
    )

    assert ServicioCuentaBancariaTercero.listar(
        tercero_id,
    ) == []


def test_direccion_guardar_y_listar(
    tercero_id,
):
    from aplicacion.maestros.terceros.servicio_registros import (
        ServicioDireccionTercero,
    )

    ServicioDireccionTercero.guardar(
        {
            "tercero_id": tercero_id,
            "etiqueta": "Bodega",
            "direccion": "Autopista Norte # 100-50",
            "ciudad": "Bogotá",
        },
    )

    direcciones = ServicioDireccionTercero.listar(
        tercero_id,
    )

    assert len(direcciones) == 1
    assert direcciones[0].etiqueta == "Bodega"


def test_direccion_exige_direccion(
    tercero_id,
):
    from aplicacion.maestros.terceros.servicio_registros import (
        ServicioDireccionTercero,
    )

    with pytest.raises(
        ValueError,
        match="direccion",
    ):

        ServicioDireccionTercero.guardar(
            {
                "tercero_id": tercero_id,
                "etiqueta": "Bodega",
            },
        )


def test_contacto_guardar_y_listar(
    tercero_id,
):
    from aplicacion.maestros.terceros.servicio_registros import (
        ServicioContactoTercero,
    )

    ServicioContactoTercero.guardar(
        {
            "tercero_id": tercero_id,
            "nombre": "Juan Pérez",
            "cargo": "Gerente",
            "correo": "juan@demo.com",
        },
    )

    contactos = ServicioContactoTercero.listar(
        tercero_id,
    )

    assert len(contactos) == 1
    assert contactos[0].nombre == "Juan Pérez"


def test_registros_de_un_tercero_no_se_mezclan_con_otro(
    tercero_id,
    requiere_postgresql,
):
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.maestros.terceros.servicio_registros import (
        ServicioCuentaBancariaTercero,
    )

    sufijo = uuid.uuid4().hex[:8]
    documento = str(
        900000000
        + int(sufijo[:6], 16) % 100000000,
    )

    otro_tercero = TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": documento,
            "tipo_tercero": "Cliente",
            "razon_social": f"Otro Tercero {sufijo}",
            "direccion": "Calle 1 # 2-3",
            "pais": "Colombia",
            "departamento": "Cundinamarca",
            "ciudad": "Bogotá",
            "correo": f"otro.{sufijo}@demo.com",
            "dias_credito": 0,
            "cupo_credito": 0,
            "resp_r99_pn": True,
        },
    )

    ServicioCuentaBancariaTercero.guardar(
        {
            "tercero_id": tercero_id,
            "banco": "Bancolombia",
            "numero_cuenta": "111",
        },
    )

    assert ServicioCuentaBancariaTercero.listar(
        otro_tercero.id,
    ) == []
