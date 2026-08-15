from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from aplicacion.modulos.ventas.facturas.integracion import (
    IntegracionFacturaVenta,
)


def test_aplicar_inventario_omitido_si_ya_aplicado():

    factura = MagicMock()
    factura.inventario_aplicado = True

    with patch(
        "aplicacion.modulos.ventas.facturas.integracion.ServicioFacturaVenta.obtener_completa",
        return_value=factura,
    ):

        resultado = IntegracionFacturaVenta.aplicar_inventario(
            1,
        )

    assert resultado == []


def test_aplicar_inventario_sin_factura():

    with patch(
        "aplicacion.modulos.ventas.facturas.integracion.ServicioFacturaVenta.obtener_completa",
        return_value=None,
    ):

        with pytest.raises(
            ValueError,
            match="No se encontró la factura",
        ):

            IntegracionFacturaVenta.aplicar_inventario(
                99,
            )


def test_confirmar_venta_pos_sin_dian_aplica_inventario():

    factura = MagicMock()
    factura.id = 5
    factura.estado = "borrador"
    factura.inventario_aplicado = False

    factura_confirmada = MagicMock()
    factura_confirmada.id = 5
    factura_confirmada.estado = "generada"

    with patch(
        "aplicacion.modulos.ventas.facturas.integracion.ServicioFacturaVenta.obtener_completa",
        side_effect=[
            factura,
            factura_confirmada,
        ],
    ), patch(
        "aplicacion.modulos.ventas.facturas.integracion.RepositorioFacturaVenta.actualizar_estado_confirmacion",
    ) as mock_estado, patch.object(
        IntegracionFacturaVenta,
        "aplicar_inventario",
    ) as mock_inventario, patch.object(
        IntegracionFacturaVenta,
        "_contabilizar_si_configurado",
    ) as mock_contabilizar:

        resultado = IntegracionFacturaVenta.confirmar_venta(
            5,
            emitir_dian=False,
        )

    mock_estado.assert_called_once_with(
        5,
        estado="generada",
    )
    mock_inventario.assert_called_once_with(
        5,
    )
    mock_contabilizar.assert_called_once_with(
        5,
    )
    assert resultado is factura_confirmada
