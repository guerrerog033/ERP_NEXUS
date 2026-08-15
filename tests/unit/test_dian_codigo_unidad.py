from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from aplicacion.integraciones.dian.generador_xml import (
    GeneradorXmlFactura,
)
from aplicacion.maestros.productos.repositorio import (
    RepositorioProducto,
)
from aplicacion.maestros.unidades_medida.repositorio import (
    UnidadMedidaRepositorio,
)


def test_codigo_unidad_sin_producto_id_usa_respaldo():
    assert GeneradorXmlFactura._codigo_unidad(None) == "94"
    assert GeneradorXmlFactura._codigo_unidad(0) == "94"


@patch.object(
    RepositorioProducto,
    "obtener_por_id",
    return_value=None,
)
def test_codigo_unidad_producto_inexistente_usa_respaldo(
    _mock_obtener,
):
    assert GeneradorXmlFactura._codigo_unidad(999) == "94"


@patch.object(
    RepositorioProducto,
    "obtener_por_id",
    return_value=SimpleNamespace(
        unidad_medida_id=None,
    ),
)
def test_codigo_unidad_producto_sin_unidad_usa_respaldo(
    _mock_obtener,
):
    assert GeneradorXmlFactura._codigo_unidad(1) == "94"


@patch.object(
    UnidadMedidaRepositorio,
    "obtener_por_id",
    return_value=None,
)
@patch.object(
    RepositorioProducto,
    "obtener_por_id",
    return_value=SimpleNamespace(
        unidad_medida_id=5,
    ),
)
def test_codigo_unidad_unidad_id_sin_fila_en_catalogo_usa_respaldo(
    _mock_producto,
    _mock_unidad,
):
    assert GeneradorXmlFactura._codigo_unidad(1) == "94"


@patch.object(
    UnidadMedidaRepositorio,
    "obtener_por_id",
    return_value=SimpleNamespace(
        codigo_dian="",
    ),
)
@patch.object(
    RepositorioProducto,
    "obtener_por_id",
    return_value=SimpleNamespace(
        unidad_medida_id=5,
    ),
)
def test_codigo_unidad_sin_codigo_dian_usa_respaldo(
    _mock_producto,
    _mock_unidad,
):
    assert GeneradorXmlFactura._codigo_unidad(1) == "94"


@patch.object(
    UnidadMedidaRepositorio,
    "obtener_por_id",
    return_value=SimpleNamespace(
        codigo_dian="LTR",
    ),
)
@patch.object(
    RepositorioProducto,
    "obtener_por_id",
    return_value=SimpleNamespace(
        unidad_medida_id=5,
    ),
)
def test_codigo_unidad_usa_codigo_real_del_producto(
    _mock_producto,
    _mock_unidad,
):
    assert GeneradorXmlFactura._codigo_unidad(1) == "LTR"
