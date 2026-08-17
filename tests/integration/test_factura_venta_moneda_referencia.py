from __future__ import annotations

import os
import uuid
from datetime import date

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


def _crear_cliente(sufijo: str):

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    documento = str(
        900000000
        + int(sufijo[:6], 16) % 99999999,
    )

    return TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": documento,
            "tipo_tercero": "Cliente",
            "razon_social": f"Cliente Moneda {sufijo}",
            "pais": "Colombia",
            "resp_r99_pn": True,
        },
    )


class TestFacturaVentaMonedaReferencia:

    def test_factura_sin_moneda_referencia_queda_en_none(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        factura = ServicioFacturaVenta.guardar_completa(
            {
                "cliente_id": cliente.id,
                "fecha": date.today(),
            },
            [
                {
                    "descripcion": "Producto de prueba",
                    "cantidad": 1,
                    "precio_unitario": 100000,
                },
            ],
        )

        assert factura.moneda_referencia is None
        assert factura.tasa_cambio_referencia is None

    def test_factura_con_moneda_referencia_se_persiste(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        factura = ServicioFacturaVenta.guardar_completa(
            {
                "cliente_id": cliente.id,
                "fecha": date.today(),
                "moneda_referencia": "usd",
                "tasa_cambio_referencia": 4000,
            },
            [
                {
                    "descripcion": "Servicio de exportación",
                    "cantidad": 1,
                    "precio_unitario": 4000000,
                },
            ],
        )

        assert factura.moneda_referencia == "USD"
        assert float(factura.tasa_cambio_referencia) == 4000.0
        assert float(factura.total) == 4000000.0

    def test_factura_con_moneda_extranjera_sin_tasa_falla(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        with pytest.raises(ValueError, match="tasa de cambio"):

            ServicioFacturaVenta.guardar_completa(
                {
                    "cliente_id": cliente.id,
                    "fecha": date.today(),
                    "moneda_referencia": "USD",
                },
                [
                    {
                        "descripcion": "Servicio de exportación",
                        "cantidad": 1,
                        "precio_unitario": 4000000,
                    },
                ],
            )

    def test_info_adicional_incluye_referencia_cuando_aplica(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.ventas.facturas.formatos_impresion import (
            _info_adicional_factura,
        )
        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        factura_con_referencia = (
            ServicioFacturaVenta.guardar_completa(
                {
                    "cliente_id": cliente.id,
                    "fecha": date.today(),
                    "moneda_referencia": "USD",
                    "tasa_cambio_referencia": 4000,
                },
                [
                    {
                        "descripcion": "Servicio de exportación",
                        "cantidad": 1,
                        "precio_unitario": 4000000,
                    },
                ],
            )
        )

        html = _info_adicional_factura(
            factura_con_referencia,
        )

        assert "USD" in html
        assert "1,000.00" in html

        factura_sin_referencia = (
            ServicioFacturaVenta.guardar_completa(
                {
                    "cliente_id": cliente.id,
                    "fecha": date.today(),
                },
                [
                    {
                        "descripcion": "Producto de prueba",
                        "cantidad": 1,
                        "precio_unitario": 100000,
                    },
                ],
            )
        )

        html_sin_referencia = _info_adicional_factura(
            factura_sin_referencia,
        )

        assert "Valor de referencia" not in html_sin_referencia
