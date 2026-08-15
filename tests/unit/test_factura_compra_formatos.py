from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from aplicacion.modulos.compras.facturas.formatos_impresion import (
    generar_html_factura_compra,
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
        "aplicacion.modulos.compras.facturas.formatos_impresion._datos_empresa",
        return_value=EMPRESA_DEMO,
    ):

        yield


def _factura(**extra):

    datos = dict(
        numero="FC000001",
        fecha=date(2026, 8, 15),
        proveedor_id=None,
        nit_proveedor="",
        razon_social_proveedor="",
        numero_proveedor="",
        cufe="",
        origen="manual",
        estado="recibida",
        subtotal=1000,
        iva=190,
        valor_retefuente=0,
        valor_reteica=0,
        valor_reteiva=0,
        total=1190,
        observaciones="",
        formato_impresion=None,
    )

    datos.update(extra)

    return SimpleNamespace(
        **datos,
    )


def _detalle():

    return SimpleNamespace(
        producto_id=None,
        descripcion="Materia prima",
        cantidad=2,
        precio_unitario=500,
        impuesto_id=None,
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
def test_generar_html_factura_compra_no_incluye_imagen(
    formato,
):
    html = generar_html_factura_compra(
        _factura(),
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
def test_generar_html_factura_compra_dice_proveedor_no_cliente(
    formato,
):
    html = generar_html_factura_compra(
        _factura(),
        [_detalle()],
        "Proveedor Demo SAS",
        formato=formato,
    )

    assert "Cliente" not in html
    assert "Proveedor" in html


def test_generar_html_factura_compra_incluye_cufe_y_numero_proveedor():

    html = generar_html_factura_compra(
        _factura(
            cufe="CUFE-ABC-123",
            numero_proveedor="FV-9999",
        ),
        [_detalle()],
        "Proveedor Demo SAS",
        formato="carta",
    )

    assert "CUFE-ABC-123" in html
    assert "FV-9999" in html
    assert "FC000001" in html


def test_generar_html_factura_compra_usa_datos_del_documento_sin_proveedor_id():
    """
    Facturas importadas por XML pueden no tener proveedor_id
    resuelto contra el maestro de terceros; en ese caso se usan
    nit_proveedor/razon_social_proveedor del propio documento.
    """
    html = generar_html_factura_compra(
        _factura(
            nit_proveedor="900555666",
            razon_social_proveedor="Proveedor XML SAS",
        ),
        [_detalle()],
        "Proveedor Demo SAS",
        formato="estandar",
    )

    assert "900555666" in html
    assert "Proveedor XML SAS" in html
