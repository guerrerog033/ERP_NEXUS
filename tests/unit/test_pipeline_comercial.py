from __future__ import annotations

from types import SimpleNamespace

from aplicacion.modulos.reportes.servicios import (
    ServicioReportes,
)


def test_etapa_pipeline_comercial_cobrado():

    factura = SimpleNamespace(
        total=100000.0,
        saldo_pendiente=0.0,
    )

    assert ServicioReportes._etapa_pipeline_comercial(
        pedido=None,
        remision=None,
        factura=factura,
    ) == "cobrado"


def test_etapa_pipeline_comercial_factura_con_saldo():

    factura = SimpleNamespace(
        total=100000.0,
        saldo_pendiente=50000.0,
    )

    assert ServicioReportes._etapa_pipeline_comercial(
        pedido=SimpleNamespace(),
        remision=SimpleNamespace(),
        factura=factura,
    ) == "factura"


def test_etapa_pipeline_comercial_remision_sin_factura():

    assert ServicioReportes._etapa_pipeline_comercial(
        pedido=SimpleNamespace(),
        remision=SimpleNamespace(),
        factura=None,
    ) == "remisión"


def test_etapa_pipeline_comercial_solo_pedido():

    assert ServicioReportes._etapa_pipeline_comercial(
        pedido=SimpleNamespace(),
        remision=None,
        factura=None,
    ) == "pedido"


def test_etapa_pipeline_comercial_solo_cotizacion():

    assert ServicioReportes._etapa_pipeline_comercial(
        pedido=None,
        remision=None,
        factura=None,
    ) == "cotización"


def test_pipeline_comercial_resumen_agrupa_etapas():

    filas = [
        {
            "etapa_actual": "cotización",
            "cotizacion_total": 100000.0,
        },
        {
            "etapa_actual": "factura",
            "cotizacion_total": 200000.0,
        },
        {
            "etapa_actual": "factura",
            "cotizacion_total": 50000.0,
        },
        {
            "etapa_actual": "cobrado",
            "cotizacion_total": 75000.0,
        },
    ]

    resumen = ServicioReportes.pipeline_comercial_resumen(
        filas,
    )

    assert resumen["cotización"]["cantidad"] == 1
    assert resumen["factura"]["cantidad"] == 2
    assert resumen["cobrado"]["cantidad"] == 1
    assert resumen["factura"]["total"] == 250000.0
