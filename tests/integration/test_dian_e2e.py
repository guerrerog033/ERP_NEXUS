from __future__ import annotations

import os
import uuid
from unittest.mock import patch

import pytest

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)
from aplicacion.integraciones.dian.cliente_emision import (
    ResultadoEmision,
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


@pytest.fixture
def sufijo_unico():
    return uuid.uuid4().hex[:8]


@patch(
    "aplicacion.modulos.ventas.facturas.integracion.ClienteEmisionDian.enviar",
)
def test_confirmar_venta_emitir_dian_mock_exito(
    mock_enviar,
    requiere_postgresql,
    sufijo_unico,
):
    from tests.integration.test_flujo_venta_basico import (
        _confirmar_cotizacion_demo,
        _crear_cotizacion_demo,
        _preparar_maestros,
    )
    from aplicacion.modulos.ventas.facturas.integracion import (
        IntegracionFacturaVenta,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )

    mock_enviar.return_value = ResultadoEmision(
        exito=True,
        estado="aceptada",
        mensaje="Documento aceptado (mock)",
        track_id="TRACK-MOCK-001",
        ruta_zip="/tmp/fv-demo.zip",
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}dian"

    _cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    _confirmar_cotizacion_demo(
        cotizacion.id,
    )

    factura = ServicioFacturaVenta.crear_desde_cotizacion(
        cotizacion.id,
    )

    factura_emitida = IntegracionFacturaVenta.confirmar_venta(
        factura.id,
        emitir_dian=True,
    )

    assert factura_emitida is not None
    assert factura_emitida.estado in (
        "emitida",
        "contabilizada",
    )
    assert str(
        factura_emitida.estado_dian or "",
    ).lower() == "aceptada"
    mock_enviar.assert_called_once()


@pytest.mark.dian
def test_confirmar_venta_emitir_dian_real_habilitacion(
    requiere_postgresql,
    sufijo_unico,
):
    if os.environ.get(
        "DIAN_E2E",
    ) != "1":

        pytest.skip(
            "Defina DIAN_E2E=1 para emisión real en habilitación",
        )

    from tests.integration.test_flujo_venta_basico import (
        _confirmar_cotizacion_demo,
        _crear_cotizacion_demo,
        _preparar_maestros,
    )
    from aplicacion.modulos.ventas.facturas.integracion import (
        IntegracionFacturaVenta,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}dianr"

    _cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    _confirmar_cotizacion_demo(
        cotizacion.id,
    )

    factura = ServicioFacturaVenta.crear_desde_cotizacion(
        cotizacion.id,
    )

    factura_emitida = IntegracionFacturaVenta.confirmar_venta(
        factura.id,
        emitir_dian=True,
    )

    assert factura_emitida is not None
    assert factura_emitida.estado in (
        "emitida",
        "generada",
        "contabilizada",
    )
    assert factura_emitida.cufe
