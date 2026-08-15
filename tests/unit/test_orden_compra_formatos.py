from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from aplicacion.modulos.compras.ordenes.formatos_impresion import (
    generar_html_orden_compra,
)

EMPRESA_DEMO = {
    "nombre": "Empresa Demo",
    "nit": "900123456",
    "direccion": "",
    "telefono": "",
    "correo": "",
    "ciudad": "",
    "pais": "Colombia",
    "notas_pie": "",
    "vendedor_nombre": "",
    "vendedor_correo": "",
    "vendedor_telefono": "",
    "logo_ruta": "",
}


@pytest.fixture(autouse=True)
def _sin_dependencia_de_bd():

    with patch(
        "aplicacion.modulos.compras.ordenes.formatos_impresion._datos_empresa",
        return_value=EMPRESA_DEMO,
    ):

        yield


def _orden():

    return SimpleNamespace(
        numero="OC000001",
        fecha=date(2026, 8, 15),
        proveedor_id=None,
        observaciones="",
        subtotal=1000,
        total=1000,
        formato_impresion=None,
    )


def _detalle():

    return SimpleNamespace(
        producto_id=None,
        descripcion="Materia prima",
        cantidad=2,
        cantidad_recibida=0,
        costo_unitario=500,
        total_linea=1000,
    )


@pytest.mark.parametrize(
    "formato",
    (
        "carta",
        "corporativo",
        "moderno",
        "compacto",
        "tirilla",
        "estandar",
    ),
)
def test_generar_html_orden_compra_no_incluye_imagen(
    formato,
):
    """
    Las órdenes de compra reusan el motor de formatos de
    cotizaciones, pero las imágenes de producto quedan exclusivas
    de Cotizaciones (decisión de producto).
    """
    html = generar_html_orden_compra(
        _orden(),
        [_detalle()],
        "Proveedor Demo SAS",
        formato=formato,
    )

    assert "background:#f8fafc;border:1px solid #e2e8f0" not in html
    assert "<img " not in html


@pytest.mark.parametrize(
    "formato",
    (
        "carta",
        "corporativo",
        "moderno",
        "compacto",
        "tirilla",
    ),
)
def test_generar_html_orden_compra_dice_proveedor_no_cliente(
    formato,
):
    html = generar_html_orden_compra(
        _orden(),
        [_detalle()],
        "Proveedor Demo SAS",
        formato=formato,
    )

    assert "Cliente" not in html
    assert "Proveedor" in html


def test_generar_html_orden_compra_incluye_numero_y_total():

    html = generar_html_orden_compra(
        _orden(),
        [_detalle()],
        "Proveedor Demo SAS",
        formato="carta",
    )

    assert "OC000001" in html
    assert "Proveedor Demo SAS" in html


def test_generar_html_orden_compra_usa_documento_proveedor_como_respaldo():

    html = generar_html_orden_compra(
        _orden(),
        [_detalle()],
        "Proveedor Demo SAS",
        documento_proveedor="900555666",
        formato="estandar",
    )

    assert "900555666" in html
