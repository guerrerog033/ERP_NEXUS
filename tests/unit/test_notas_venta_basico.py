from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from aplicacion.modulos.ventas.notas_credito.integracion import (
    IntegracionNotaCreditoVenta,
)
from aplicacion.modulos.ventas.notas_credito.servicios import (
    ServicioNotaCreditoVenta,
)
from aplicacion.modulos.ventas.notas_debito.integracion import (
    IntegracionNotaDebitoVenta,
)
from aplicacion.modulos.ventas.notas_debito.servicios import (
    ServicioNotaDebitoVenta,
)


def _factura_mock(
    *,
    estado: str = "contabilizada",
):
    detalle = SimpleNamespace(
        producto_id=99,
        producto_variante_id=None,
        descripcion="Producto demo",
        cantidad=1.0,
        precio_unitario=25000.0,
        impuesto_id=1,
        precio_incluye_iva=False,
        total_linea=29750.0,
    )

    return SimpleNamespace(
        id=7,
        numero="FV-00007",
        cliente_id=5,
        estado=estado,
        cufe="CUFE-DEMO",
        detalles=[detalle],
        retefuente_id=None,
        reteica_id=None,
        reteiva_id=None,
    )


@patch.object(
    ServicioNotaCreditoVenta.repositorio,
    "siguiente_secuencia",
    return_value=1,
)
@patch.object(
    ServicioNotaCreditoVenta.repositorio,
    "guardar_completa",
)
@patch(
    "aplicacion.modulos.ventas.notas_credito.servicios.ServicioFacturaVenta.obtener_completa",
)
def test_crear_nota_credito_desde_factura_contabilizada(
    mock_obtener_factura,
    mock_guardar,
    _mock_secuencia,
):
    mock_obtener_factura.return_value = _factura_mock()

    nota_guardada = MagicMock(
        id=1,
        factura_id=7,
    )
    mock_guardar.return_value = nota_guardada

    resultado = ServicioNotaCreditoVenta.crear_desde_factura(
        7,
        motivo="Devolución parcial",
    )

    assert resultado is nota_guardada

    cabecera, lineas = mock_guardar.call_args[0]

    assert cabecera["factura_id"] == 7
    assert cabecera["cliente_id"] == 5
    assert len(lineas) == 1


@patch.object(
    ServicioNotaDebitoVenta.repositorio,
    "siguiente_secuencia",
    return_value=1,
)
@patch.object(
    ServicioNotaDebitoVenta.repositorio,
    "guardar_completa",
)
@patch(
    "aplicacion.modulos.ventas.notas_debito.servicios.ServicioFacturaVenta.obtener_completa",
)
def test_crear_nota_debito_desde_factura_contabilizada(
    mock_obtener_factura,
    mock_guardar,
    _mock_secuencia,
):
    mock_obtener_factura.return_value = _factura_mock()

    nota_guardada = MagicMock(
        id=2,
        factura_id=7,
    )
    mock_guardar.return_value = nota_guardada

    resultado = ServicioNotaDebitoVenta.crear_desde_factura(
        7,
        motivo="Intereses mora",
    )

    assert resultado is nota_guardada

    cabecera, lineas = mock_guardar.call_args[0]

    assert cabecera["factura_id"] == 7
    assert cabecera["cliente_id"] == 5
    assert len(lineas) == 1


@patch(
    "aplicacion.modulos.ventas.notas_credito.servicios.ServicioFacturaVenta.obtener_completa",
)
def test_crear_nota_credito_rechaza_factura_borrador(
    mock_obtener_factura,
):
    mock_obtener_factura.return_value = _factura_mock(
        estado="borrador",
    )

    with pytest.raises(
        ValueError,
        match="confirmada",
    ):
        ServicioNotaCreditoVenta.crear_desde_factura(
            7,
        )


@patch.object(
    IntegracionNotaCreditoVenta,
    "_contabilizar_si_configurado",
)
@patch.object(
    IntegracionNotaCreditoVenta,
    "_aplicar_efectos_operativos",
)
@patch(
    "aplicacion.modulos.ventas.notas_credito.integracion.ServicioNotaCreditoVenta.obtener_completa",
)
@patch(
    "aplicacion.modulos.ventas.notas_credito.integracion.RepositorioNotaCreditoVenta.actualizar_estado_confirmacion",
)
def test_confirmar_nota_credito_aplica_efectos_y_contabiliza(
    mock_estado,
    mock_obtener,
    mock_efectos,
    mock_contabilizar,
):
    from aplicacion.modulos.ventas.notas_credito.integracion import (
        IntegracionNotaCreditoVenta,
    )

    nota_borrador = SimpleNamespace(
        id=3,
        estado="borrador",
    )
    nota_generada = SimpleNamespace(
        id=3,
        estado="generada",
    )

    mock_obtener.side_effect = [
        nota_borrador,
        nota_generada,
    ]

    resultado = IntegracionNotaCreditoVenta.confirmar_generacion(
        3,
        emitir_dian=False,
    )

    mock_estado.assert_called_once_with(
        3,
        estado="generada",
    )
    mock_efectos.assert_called_once_with(
        3,
    )
    mock_contabilizar.assert_called_once_with(
        3,
    )
    assert resultado is nota_generada


@patch.object(
    IntegracionNotaDebitoVenta,
    "_contabilizar_si_configurado",
)
@patch.object(
    IntegracionNotaDebitoVenta,
    "_aplicar_efectos_operativos",
)
@patch(
    "aplicacion.modulos.ventas.notas_debito.integracion.ServicioNotaDebitoVenta.obtener_completa",
)
@patch(
    "aplicacion.modulos.ventas.notas_debito.integracion.RepositorioNotaDebitoVenta.actualizar_estado_confirmacion",
)
def test_confirmar_nota_debito_aplica_saldo_y_contabiliza(
    mock_estado,
    mock_obtener,
    mock_efectos,
    mock_contabilizar,
):
    from aplicacion.modulos.ventas.notas_debito.integracion import (
        IntegracionNotaDebitoVenta,
    )

    nota_borrador = SimpleNamespace(
        id=4,
        estado="borrador",
    )
    nota_generada = SimpleNamespace(
        id=4,
        estado="generada",
    )

    mock_obtener.side_effect = [
        nota_borrador,
        nota_generada,
    ]

    resultado = IntegracionNotaDebitoVenta.confirmar_generacion(
        4,
        emitir_dian=False,
    )

    mock_estado.assert_called_once_with(
        4,
        estado="generada",
    )
    mock_efectos.assert_called_once_with(
        4,
        aplicar_saldo=True,
    )
    mock_contabilizar.assert_called_once_with(
        4,
    )
    assert resultado is nota_generada
