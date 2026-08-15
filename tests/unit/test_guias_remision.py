from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch


@patch(
    "aplicacion.integraciones.dian.generador_guia_remision.Configuracion.obtener",
    side_effect=lambda seccion, clave, default=None: {
        ("empresa", "nit"): "900000001",
        ("empresa", "nombre"): "Empresa Test",
        ("empresa", "direccion"): "Calle 1",
        ("empresa", "ciudad"): "Bogotá",
        ("empresa", "departamento"): "Cundinamarca",
        ("dian", "ambiente"): "habilitacion",
    }.get((seccion, clave), default),
)
def test_generador_guia_remision_cude(
    _mock_config,
):

    from aplicacion.integraciones.dian.generador_guia_remision import (
        GeneradorGuiaRemision,
    )

    guia = MagicMock()
    guia.numero = "GRE000001"
    guia.fecha = date(2026, 8, 10)
    guia.total = 1000
    guia.subtotal = 1000
    guia.direccion_origen = "Calle 1"
    guia.ciudad_origen = "Bogotá"
    guia.departamento_origen = "Cundinamarca"
    guia.direccion_destino = "Calle 2"
    guia.ciudad_destino = "Medellín"
    guia.departamento_destino = "Antioquia"
    guia.conductor = "Juan Pérez"
    guia.vehiculo = "Camión"
    guia.placa = "ABC123"
    guia.transportadora = "Transportes SA"

    detalle = MagicMock()
    detalle.producto_id = None
    detalle.descripcion = "Producto A"
    detalle.cantidad = 2
    detalle.precio_unitario = 500
    detalle.total_linea = 1000

    guia.detalles = [detalle]

    datos = GeneradorGuiaRemision.generar(
        guia,
        nit_cliente="900123456",
        razon_cliente="Cliente SA",
    )

    assert datos.cude
    assert "DespatchAdvice" in datos.xml
    assert "GRE000001" in datos.xml
