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
            "razon_social": f"Contraparte Demo {sufijo}",
            "direccion": "Calle 1 # 2-3",
            "pais": "Colombia",
            "departamento": "Cundinamarca",
            "ciudad": "Bogotá",
            "correo": f"cliente.{sufijo}@demo.com",
            "dias_credito": 0,
            "cupo_credito": 0,
            "resp_r99_pn": True,
        },
    )


def test_recibo_caja_anticipo_persiste_formato_y_se_usa_al_imprimir(
    requiere_postgresql,
):
    from aplicacion.modulos.tesoreria.recibos_caja.formatos_impresion import (
        generar_html_recibo,
    )
    from aplicacion.modulos.tesoreria.recibos_caja.servicios import (
        ServicioReciboCaja,
    )

    sufijo = uuid.uuid4().hex[:8]

    cliente = _crear_cliente(
        sufijo,
    )

    recibo = ServicioReciboCaja.guardar_completo(
        {
            "cliente_id": cliente.id,
            "forma_pago": "efectivo",
            "formato_impresion": "moderno",
            "es_anticipo": True,
            "valor_total": 80000,
        },
        [],
    )

    assert recibo.formato_impresion == "moderno"

    recibo_completo = ServicioReciboCaja.obtener_completo(
        recibo.id,
    )

    assert recibo_completo.formato_impresion == "moderno"

    html = generar_html_recibo(
        recibo_completo,
        nombre_cliente=cliente.razon_social,
    )

    assert "Recibimos de" in html
    assert "Cliente" not in html
    assert "background:#f8fafc;border:1px solid #e2e8f0" not in html
    assert recibo.numero in html
    assert "Abono / anticipo sin factura" in html
