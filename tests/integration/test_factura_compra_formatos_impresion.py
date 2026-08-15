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


def _crear_proveedor(sufijo: str):
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
            "tipo_tercero": "Proveedor",
            "razon_social": f"Proveedor Demo {sufijo}",
            "direccion": "Calle 1 # 2-3",
            "pais": "Colombia",
            "departamento": "Cundinamarca",
            "ciudad": "Bogotá",
            "correo": f"proveedor.{sufijo}@demo.com",
            "dias_credito": 0,
            "cupo_credito": 0,
            "resp_r99_pn": True,
        },
    )


def test_factura_compra_persiste_formato_y_se_usa_al_imprimir(
    requiere_postgresql,
):
    from aplicacion.modulos.compras.facturas.formatos_impresion import (
        generar_html_factura_compra,
    )
    from aplicacion.modulos.compras.facturas.servicios import (
        ServicioFacturaCompra,
    )

    sufijo = uuid.uuid4().hex[:8]

    proveedor = _crear_proveedor(
        sufijo,
    )

    factura = ServicioFacturaCompra.guardar_completa(
        {
            "proveedor_id": proveedor.id,
            "formato_impresion": "moderno",
        },
        [
            {
                "descripcion": "Materia prima",
                "cantidad": 3,
                "precio_unitario": 500,
            },
        ],
    )

    assert factura.formato_impresion == "moderno"

    factura_completa = ServicioFacturaCompra.obtener_completa(
        factura.id,
    )

    assert factura_completa.formato_impresion == "moderno"

    html = generar_html_factura_compra(
        factura_completa,
        list(
            factura_completa.detalles,
        ),
        proveedor.razon_social,
    )

    assert "Proveedor" in html
    assert "Cliente" not in html
    assert "background:#f8fafc;border:1px solid #e2e8f0" not in html
    assert factura.numero in html
