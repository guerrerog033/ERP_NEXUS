from __future__ import annotations

import os
import uuid
from datetime import date, timedelta

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


def _sufijo() -> str:

    return uuid.uuid4().hex[:8]


def _documento(sufijo: str) -> str:

    return str(
        900000000
        + int(sufijo[:6], 16) % 99999999,
    )


def _crear_cliente(
    sufijo: str,
    *,
    exento: bool = False,
):

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    return TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": _documento(sufijo),
            "tipo_tercero": "Cliente",
            "razon_social": f"Bloqueo Cartera Demo {sufijo}",
            "pais": "Colombia",
            "resp_r99_pn": True,
            "exento_bloqueo_cartera": exento,
        },
    )


def _crear_factura_vencida(
    cliente_id: int,
    *,
    dias_vencido: int = 30,
):

    from aplicacion.base_datos.conexion import SessionLocal
    from aplicacion.modulos.ventas.facturas.modelos import (
        FacturaVenta,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )

    fecha = date.today() - timedelta(
        days=dias_vencido,
    )

    factura = ServicioFacturaVenta.guardar_completa(
        {
            "cliente_id": cliente_id,
            "fecha": fecha,
            "fecha_vencimiento": fecha,
        },
        [
            {
                "descripcion": "Producto de prueba",
                "cantidad": 1,
                "precio_unitario": 100000,
            },
        ],
    )

    db = SessionLocal()

    try:

        registro = (
            db.query(FacturaVenta)
            .filter(FacturaVenta.id == factura.id)
            .one()
        )

        registro.contabilizado = True

        db.commit()

    finally:

        db.close()

    return factura


def _habilitar_bloqueo(
    monkeypatch,
    *,
    dias_gracia: int = 0,
):

    from aplicacion.nucleo.configuracion import (
        Configuracion,
    )

    datos = Configuracion.cargar()

    monkeypatch.setitem(
        datos,
        "cartera",
        {
            "bloquear_facturacion_por_mora": True,
            "dias_gracia_mora": dias_gracia,
        },
    )


def _deshabilitar_bloqueo(
    monkeypatch,
):

    from aplicacion.nucleo.configuracion import (
        Configuracion,
    )

    datos = Configuracion.cargar()

    monkeypatch.setitem(
        datos,
        "cartera",
        {
            "bloquear_facturacion_por_mora": False,
        },
    )


def _nueva_factura(cliente_id: int):

    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )

    return ServicioFacturaVenta.guardar_completa(
        {
            "cliente_id": cliente_id,
            "fecha": date.today(),
        },
        [
            {
                "descripcion": "Otro producto",
                "cantidad": 1,
                "precio_unitario": 50000,
            },
        ],
    )


class TestServicioCarteraVerificarBloqueoPorMora:

    def test_bloquea_nueva_factura_si_hay_cartera_vencida(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        _crear_factura_vencida(
            cliente.id,
            dias_vencido=30,
        )

        _habilitar_bloqueo(monkeypatch)

        with pytest.raises(
            ValueError,
            match="cartera vencida",
        ):

            _nueva_factura(cliente.id)

    def test_no_bloquea_si_configuracion_deshabilitada(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        _crear_factura_vencida(
            cliente.id,
            dias_vencido=30,
        )

        _deshabilitar_bloqueo(monkeypatch)

        factura = _nueva_factura(cliente.id)

        assert factura.id is not None

    def test_no_bloquea_cliente_exento(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        sufijo = _sufijo()

        cliente = _crear_cliente(
            sufijo,
            exento=True,
        )

        _crear_factura_vencida(
            cliente.id,
            dias_vencido=30,
        )

        _habilitar_bloqueo(monkeypatch)

        factura = _nueva_factura(cliente.id)

        assert factura.id is not None

    def test_no_bloquea_dentro_de_dias_gracia(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        _crear_factura_vencida(
            cliente.id,
            dias_vencido=5,
        )

        _habilitar_bloqueo(
            monkeypatch,
            dias_gracia=10,
        )

        factura = _nueva_factura(cliente.id)

        assert factura.id is not None

    def test_permite_actualizar_factura_existente_aunque_haya_mora(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        factura_vencida = _crear_factura_vencida(
            cliente.id,
            dias_vencido=30,
        )

        _habilitar_bloqueo(monkeypatch)

        cabecera = {
            "cliente_id": cliente.id,
            "numero": factura_vencida.numero,
        }

        ServicioFacturaVenta.validar_cabecera(
            cabecera,
            id_registro=factura_vencida.id,
        )
