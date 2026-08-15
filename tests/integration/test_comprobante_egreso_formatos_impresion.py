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


def test_comprobante_egreso_anticipo_persiste_formato_y_se_usa_al_imprimir(
    requiere_postgresql,
):
    from aplicacion.modulos.tesoreria.comprobantes_egreso.formatos_impresion import (
        generar_html_comprobante,
    )
    from aplicacion.modulos.tesoreria.comprobantes_egreso.servicios import (
        ServicioComprobanteEgreso,
    )

    sufijo = uuid.uuid4().hex[:8]

    proveedor = _crear_proveedor(
        sufijo,
    )

    comprobante = ServicioComprobanteEgreso.guardar_completo(
        {
            "proveedor_id": proveedor.id,
            "forma_pago": "transferencia",
            "formato_impresion": "moderno",
            "es_anticipo": True,
            "valor_total": 60000,
        },
        [],
    )

    assert comprobante.formato_impresion == "moderno"

    comprobante_completo = (
        ServicioComprobanteEgreso.obtener_completo(
            comprobante.id,
        )
    )

    assert comprobante_completo.formato_impresion == "moderno"

    html = generar_html_comprobante(
        comprobante_completo,
        nombre_proveedor=proveedor.razon_social,
    )

    assert "Pagado a" in html
    assert "Cliente" not in html
    assert "background:#f8fafc;border:1px solid #e2e8f0" not in html
    assert comprobante.numero in html
    assert "Anticipo / abono sin factura" in html
