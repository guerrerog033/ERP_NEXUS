from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from aplicacion.modulos.gerencial.servicios import (
    ServicioPanelGerencial,
)
from aplicacion.modulos.gerencial.vista import (
    PanelGerencialPage,
)


pytestmark = pytest.mark.usefixtures(
    "qapp",
)


def test_servicio_panel_gerencial_incluye_pipeline_periodo(
    monkeypatch,
):
    monkeypatch.setattr(
        "aplicacion.modulos.gerencial.servicios.obtener_resumen_inicio",
        lambda: MagicMock(
            empresa_nombre="Empresa Demo",
            cxc_total=1000.0,
            cxp_total=500.0,
            cxc_vencido=200.0,
            cotizaciones_mes_total=3,
            productos_activos=10,
        ),
    )
    monkeypatch.setattr(
        ServicioPanelGerencial,
        "_pipeline_periodo",
        classmethod(
            lambda cls, fecha_desde, fecha_hasta: {
                "cotizaciones": 2,
                "total_cotizado": 300000.0,
                "total_cobrado": 150000.0,
                "etapas": {
                    "cotización": {
                        "cantidad": 1,
                        "total": 100000.0,
                    },
                },
                "periodo_desde": fecha_desde,
                "periodo_hasta": fecha_hasta,
            },
        ),
    )

    class _Consulta:

        def filter(self, *args, **kwargs):

            return self

        def order_by(self, *args, **kwargs):

            return self

        def limit(self, *args, **kwargs):

            return self

        def all(self):

            return []

    class _Db:

        def query(self, *args, **kwargs):

            return _Consulta()

        def close(self):

            return None

    monkeypatch.setattr(
        "aplicacion.modulos.gerencial.servicios.SessionLocal",
        _Db,
    )

    resumen = ServicioPanelGerencial.resumen()

    assert resumen["empresa"] == "Empresa Demo"
    assert resumen["pipeline_periodo"]["cotizaciones"] == 2
    assert resumen["pipeline_periodo"]["total_cobrado"] == 150000.0
    assert resumen["utilidad_estimada"] == 0


def _resumen_mock(**overrides):

    base = {
        "empresa": "Empresa Demo",
        "ventas_dia": 250000.0,
        "compras_dia": 100000.0,
        "utilidad_estimada": 150000.0,
        "cxc_total": 1000000.0,
        "cxc_vencido": 100000.0,
        "cxp_total": 500000.0,
        "productos_activos": 12,
        "top_productos": [],
        "variacion_periodo_anterior": {},
        "serie_mensual": [],
        "periodo_desde": None,
        "periodo_hasta": None,
        "pipeline_periodo": {
            "cotizaciones": 4,
            "total_cotizado": 800000.0,
            "total_cobrado": 200000.0,
            "etapas": {
                "factura": {
                    "cantidad": 2,
                    "total": 400000.0,
                },
            },
        },
    }
    base.update(overrides)

    return base


def test_panel_gerencial_page_muestra_empresa_y_periodo(
    monkeypatch,
):
    monkeypatch.setattr(
        ServicioPanelGerencial,
        "resumen",
        classmethod(
            lambda cls, **kwargs: _resumen_mock(
                periodo_desde=kwargs.get("fecha_desde"),
                periodo_hasta=kwargs.get("fecha_hasta"),
            ),
        ),
    )

    pagina = PanelGerencialPage()

    assert "Empresa Demo" in pagina.lbl_empresa.text()
    assert pagina.grid.count() >= 6


def test_panel_gerencial_page_muestra_top_productos_y_grafico(
    monkeypatch,
):
    monkeypatch.setattr(
        ServicioPanelGerencial,
        "resumen",
        classmethod(
            lambda cls, **kwargs: _resumen_mock(
                top_productos=[
                    {
                        "nombre": "Producto A",
                        "cantidad": 10,
                        "valor": 500000.0,
                    },
                ],
                serie_mensual=[
                    {
                        "anio": 2026,
                        "mes": 7,
                        "ventas": 1000000.0,
                        "compras": 400000.0,
                    },
                    {
                        "anio": 2026,
                        "mes": 8,
                        "ventas": 1200000.0,
                        "compras": 500000.0,
                    },
                ],
                variacion_periodo_anterior={
                    "cotizado": 12.5,
                    "cobrado": -8.0,
                },
            ),
        ),
    )

    pagina = PanelGerencialPage()

    tabla = pagina._construir_top_productos(
        [
            {
                "nombre": "Producto A",
                "cantidad": 10,
                "valor": 500000.0,
            },
        ],
    )

    assert tabla is not None

    grafico = pagina._construir_grafico_mensual(
        [
            {
                "anio": 2026,
                "mes": 7,
                "ventas": 1000000.0,
                "compras": 400000.0,
            },
        ],
    )

    assert grafico is not None


def test_panel_gerencial_page_sin_ventas_no_muestra_grafico(
    monkeypatch,
):
    monkeypatch.setattr(
        ServicioPanelGerencial,
        "resumen",
        classmethod(
            lambda cls, **kwargs: _resumen_mock(),
        ),
    )

    pagina = PanelGerencialPage()

    assert pagina._construir_grafico_mensual([]) is None


def test_variacion_periodo_anterior_calcula_porcentaje(
    monkeypatch,
):
    from datetime import date

    monkeypatch.setattr(
        ServicioPanelGerencial,
        "_pipeline_periodo",
        classmethod(
            lambda cls, fecha_desde, fecha_hasta: {
                "total_cotizado": 100000.0,
                "total_cobrado": 50000.0,
            },
        ),
    )

    variacion = ServicioPanelGerencial._variacion_periodo_anterior(
        date(2026, 8, 1),
        date(2026, 8, 31),
        {
            "total_cotizado": 150000.0,
            "total_cobrado": 25000.0,
        },
    )

    assert variacion["cotizado"] == pytest.approx(50.0)
    assert variacion["cobrado"] == pytest.approx(-50.0)


def test_variacion_periodo_anterior_sin_datos_previos_retorna_none(
    monkeypatch,
):
    from datetime import date

    monkeypatch.setattr(
        ServicioPanelGerencial,
        "_pipeline_periodo",
        classmethod(
            lambda cls, fecha_desde, fecha_hasta: {
                "total_cotizado": 0.0,
                "total_cobrado": 0.0,
            },
        ),
    )

    variacion = ServicioPanelGerencial._variacion_periodo_anterior(
        date(2026, 8, 1),
        date(2026, 8, 31),
        {
            "total_cotizado": 150000.0,
            "total_cobrado": 25000.0,
        },
    )

    assert variacion["cotizado"] is None
    assert variacion["cobrado"] is None
