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


def _crear_producto(sufijo: str):
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )

    return ServicioProducto.guardar_completo(
        {
            "codigo": f"OCF{sufijo.upper()}",
            "nombre": f"Producto OC Demo {sufijo}",
            "tipo": "producto",
            "precio_venta": 1000,
            "precio_incluye_iva": False,
            "costo": 500,
            "existencia": 0,
            "stock_minimo": 0,
            "activo": True,
            "maneja_variantes": False,
        },
    )


def test_orden_compra_persiste_formato_y_se_usa_al_imprimir(
    requiere_postgresql,
):
    from aplicacion.modulos.compras.ordenes.formatos_impresion import (
        generar_html_orden_compra,
    )
    from aplicacion.modulos.compras.ordenes.servicios import (
        ServicioOrdenCompra,
    )

    sufijo = uuid.uuid4().hex[:8]

    proveedor = _crear_proveedor(
        sufijo,
    )

    producto = _crear_producto(
        sufijo,
    )

    orden = ServicioOrdenCompra.guardar(
        proveedor_id=proveedor.id,
        fecha=date.today(),
        observaciones="Prueba de formato",
        lineas=[
            {
                "producto_id": producto.id,
                "descripcion": producto.nombre,
                "cantidad": 3,
                "costo_unitario": 500,
            },
        ],
        formato_impresion="moderno",
    )

    assert orden.formato_impresion == "moderno"

    (
        orden_completa,
        detalles,
        nombre_proveedor,
        _proveedor_obj,
    ) = ServicioOrdenCompra.datos_impresion(
        orden.id,
    )

    assert orden_completa.formato_impresion == "moderno"

    html = generar_html_orden_compra(
        orden_completa,
        detalles,
        nombre_proveedor,
    )

    assert "Proveedor" in html
    assert "Cliente" not in html
    assert "background:#f8fafc;border:1px solid #e2e8f0" not in html
    assert orden.numero in html
