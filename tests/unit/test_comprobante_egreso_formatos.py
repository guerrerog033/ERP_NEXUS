from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from aplicacion.modulos.tesoreria.comprobantes_egreso.formatos_impresion import (
    generar_html_comprobante,
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
        "aplicacion.modulos.tesoreria.comprobantes_egreso.formatos_impresion._datos_empresa",
        return_value=EMPRESA_DEMO,
    ):

        yield


def _comprobante(**extra):

    datos = dict(
        numero="CE000001",
        fecha=date(2026, 8, 15),
        proveedor_id=None,
        forma_pago="transferencia",
        valor_total=50000,
        observaciones="",
        detalles=[],
        formato_impresion=None,
    )

    datos.update(extra)

    return SimpleNamespace(
        **datos,
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
def test_generar_html_comprobante_no_incluye_imagen(
    formato,
):
    html = generar_html_comprobante(
        _comprobante(),
        nombre_proveedor="Contraparte Demo SAS",
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
def test_generar_html_comprobante_dice_pagado_a_no_cliente(
    formato,
):
    html = generar_html_comprobante(
        _comprobante(),
        nombre_proveedor="Contraparte Demo SAS",
        formato=formato,
    )

    assert "Cliente" not in html
    assert "Pagado a" in html


def test_generar_html_comprobante_anticipo_muestra_linea_sintetica():

    html = generar_html_comprobante(
        _comprobante(
            valor_total=95000,
        ),
        nombre_proveedor="Contraparte Demo SAS",
        formato="carta",
    )

    assert "Anticipo / abono sin factura" in html
    assert "95,000.00" in html


def test_generar_html_comprobante_sin_valor_ni_detalles_no_muestra_lineas():

    html = generar_html_comprobante(
        _comprobante(
            valor_total=0,
        ),
        nombre_proveedor="Contraparte Demo SAS",
        formato="carta",
    )

    assert "Anticipo / abono sin factura" not in html


def test_generar_html_comprobante_incluye_forma_de_pago_y_numero():

    html = generar_html_comprobante(
        _comprobante(
            forma_pago="cheque",
        ),
        nombre_proveedor="Contraparte Demo SAS",
        formato="carta",
    )

    assert "Cheque" in html
    assert "CE000001" in html


def test_generar_html_comprobante_usa_documento_proveedor_como_respaldo():

    html = generar_html_comprobante(
        _comprobante(),
        nombre_proveedor="Contraparte Demo SAS",
        documento_proveedor="900555666",
        formato="estandar",
    )

    assert "900555666" in html
