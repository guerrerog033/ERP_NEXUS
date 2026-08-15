"""Tests del puente HTML canónico (DTO → vista previa)."""

from __future__ import annotations

from aplicacion.reportes.comunes.html_documento import (
    contexto_formato_desde_dto,
    dto_a_cliente_html,
    dto_a_resumen_html,
    filas_tabla_cartera_html,
    html_comercial_desde_dto,
)


def test_dto_a_cliente_html_mapea_documento():

    cliente = dto_a_cliente_html(
        {
            "nombre": "Cliente Demo",
            "documento": "900123456-7",
            "direccion": "Calle 1",
            "ciudad": "Bogotá",
        },
    )

    assert cliente["nombre"] == "Cliente Demo"
    assert cliente["nit"] == "900123456-7"


def test_dto_a_resumen_html():

    resumen = dto_a_resumen_html(
        {
            "subtotal": 100000,
            "impuestos": 19000,
            "total": 119000,
        },
    )

    assert resumen["subtotal"] == 100000.0
    assert resumen["iva"] == 19000.0
    assert resumen["total"] == 119000.0


def test_contexto_formato_desde_dto():

    dto = {
        "numero": "PED-001",
        "fecha": "14/08/2026",
        "subtotal": 100000,
        "impuestos": 0,
        "total": 100000,
        "observaciones": "Entrega parcial",
        "cliente": {
            "nombre": "Cliente Demo",
            "documento": "800111222",
        },
    }

    ctx = contexto_formato_desde_dto(
        dto,
        documento=object(),
        detalles=[],
        nombre_cliente="Cliente Demo",
        etiqueta_documento="PEDIDO",
        titulo_documento="Pedido",
        empresa={
            "nombre": "Empresa Demo",
            "nit": "900123456",
        },
    )

    assert ctx.fecha == "14/08/2026"
    assert ctx.cliente["nombre"] == "Cliente Demo"
    assert ctx.resumen["total"] == 100000.0


def test_html_comercial_desde_dto_incluye_totales():

    html = html_comercial_desde_dto(
        {
            "numero": "COT-001",
            "fecha": "14/08/2026",
            "subtotal": 100000,
            "impuestos": 19000,
            "total": 119000,
            "total_letras": "CIENTO DIECINUEVE MIL",
            "cliente": {
                "nombre": "Cliente Demo",
                "documento": "800111222",
            },
            "items": [
                {
                    "descripcion": "Servicio",
                    "cantidad": 1,
                    "precio": 100000,
                    "total": 100000,
                },
            ],
        },
        titulo_documento="COTIZACIÓN",
        empresa={
            "nombre": "Empresa Demo",
            "nit": "900123456",
        },
    )

    assert "COTIZACIÓN" in html
    assert "COT-001" in html
    assert "CIENTO DIECINUEVE MIL" in html


def test_filas_tabla_cartera_html():

    filas = filas_tabla_cartera_html(
        [
            {
                "documento": "Factura FV-001",
                "saldo_anterior": 350000,
                "valor_aplicado": 150000,
                "saldo_restante": 200000,
            },
        ],
    )

    assert "Factura FV-001" in filas
    assert "$150,000.00" in filas
