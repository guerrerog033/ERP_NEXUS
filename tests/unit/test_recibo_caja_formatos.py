from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from aplicacion.modulos.tesoreria.recibos_caja.formatos_impresion import (
    generar_html_recibo,
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
        "aplicacion.modulos.tesoreria.recibos_caja.formatos_impresion._datos_empresa",
        return_value=EMPRESA_DEMO,
    ):

        yield


def _recibo(**extra):

    datos = dict(
        numero="RC000001",
        fecha=date(2026, 8, 15),
        cliente_id=None,
        forma_pago="efectivo",
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
def test_generar_html_recibo_no_incluye_imagen(
    formato,
):
    html = generar_html_recibo(
        _recibo(),
        nombre_cliente="Contraparte Demo SAS",
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
def test_generar_html_recibo_dice_recibimos_de_no_cliente(
    formato,
):
    html = generar_html_recibo(
        _recibo(),
        nombre_cliente="Contraparte Demo SAS",
        formato=formato,
    )

    assert "Cliente" not in html
    assert "Recibimos de" in html


def test_generar_html_recibo_anticipo_muestra_linea_sintetica():

    html = generar_html_recibo(
        _recibo(
            valor_total=75000,
        ),
        nombre_cliente="Contraparte Demo SAS",
        formato="carta",
    )

    assert "Abono / anticipo sin factura" in html
    assert "75,000.00" in html


def test_generar_html_recibo_sin_valor_ni_detalles_no_muestra_lineas():

    html = generar_html_recibo(
        _recibo(
            valor_total=0,
        ),
        nombre_cliente="Contraparte Demo SAS",
        formato="carta",
    )

    assert "Abono / anticipo sin factura" not in html


def test_generar_html_recibo_incluye_forma_de_pago_y_numero():

    html = generar_html_recibo(
        _recibo(
            forma_pago="transferencia_bancaria",
        ),
        nombre_cliente="Contraparte Demo SAS",
        formato="carta",
    )

    assert "Transferencia Bancaria" in html
    assert "RC000001" in html
