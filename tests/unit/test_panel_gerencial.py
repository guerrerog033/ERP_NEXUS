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


def test_panel_gerencial_page_muestra_empresa_y_periodo(
    monkeypatch,
):
    monkeypatch.setattr(
        ServicioPanelGerencial,
        "resumen",
        classmethod(
            lambda cls, **kwargs: {
                "empresa": "Empresa Demo",
                "ventas_dia": 250000.0,
                "compras_dia": 100000.0,
                "utilidad_estimada": 150000.0,
                "cxc_total": 1000000.0,
                "cxc_vencido": 100000.0,
                "cxp_total": 500000.0,
                "productos_activos": 12,
                "top_productos": [],
                "periodo_desde": kwargs.get(
                    "fecha_desde",
                ),
                "periodo_hasta": kwargs.get(
                    "fecha_hasta",
                ),
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
            },
        ),
    )

    pagina = PanelGerencialPage()

    assert "Empresa Demo" in pagina.lbl_empresa.text()
    assert pagina.grid.count() >= 6
