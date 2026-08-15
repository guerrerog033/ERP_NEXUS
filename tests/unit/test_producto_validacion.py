from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from aplicacion.maestros.productos.producto_definition import (
    ProductoDefinition,
)
from aplicacion.maestros.productos.servicios import (
    ServicioProducto,
)
from aplicacion.maestros.unidades_medida.repositorio import (
    UnidadMedidaRepositorio,
)


@pytest.fixture(autouse=True)
def _mock_unidad_medida(monkeypatch):
    monkeypatch.setattr(
        UnidadMedidaRepositorio,
        "obtener_por_codigo",
        classmethod(
            lambda cls, codigo: SimpleNamespace(
                id=1,
                codigo=codigo,
            ),
        ),
    )
    monkeypatch.setattr(
        UnidadMedidaRepositorio,
        "obtener_por_id",
        classmethod(
            lambda cls, id_registro: SimpleNamespace(
                id=id_registro,
            ),
        ),
    )


def _datos_producto_base(**extra):
    datos = {
        "codigo": "PRD001",
        "nombre": "Producto demo",
        "tipo": "producto",
        "precio_venta": 10000,
        "precio_incluye_iva": False,
        "costo": 5000,
        "existencia": 25,
        "stock_minimo": 5,
        "impuesto_venta_id": 1,
        "impuesto_compra_id": None,
        "activo": True,
        "maneja_variantes": False,
    }

    datos.update(
        extra,
    )

    return datos


@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "codigo_automatico_habilitado",
    return_value=False,
)
def test_producto_validar_requiere_codigo(
    _mock_auto,
    _mock_codigo,
):
    with pytest.raises(
        ValueError,
        match="código",
    ):
        ServicioProducto.validar(
            _datos_producto_base(
                codigo="",
            ),
        )


@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "codigo_automatico_habilitado",
    return_value=False,
)
def test_producto_validar_requiere_nombre(
    _mock_auto,
    _mock_codigo,
):
    with pytest.raises(
        ValueError,
        match="nombre",
    ):
        ServicioProducto.validar(
            _datos_producto_base(
                nombre="",
            ),
        )


@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=True,
)
@patch.object(
    ServicioProducto,
    "codigo_automatico_habilitado",
    return_value=False,
)
def test_producto_validar_rechaza_codigo_duplicado(
    _mock_auto,
    _mock_codigo,
):
    with pytest.raises(
        ValueError,
        match="código",
    ):
        ServicioProducto.validar(
            _datos_producto_base(),
        )


@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo_barras",
    return_value=True,
)
@patch.object(
    ServicioProducto,
    "codigo_automatico_habilitado",
    return_value=False,
)
def test_producto_validar_rechaza_codigo_barras_duplicado(
    _mock_auto,
    _mock_barras,
    _mock_codigo,
):
    with pytest.raises(
        ValueError,
        match="código de barras",
    ):
        ServicioProducto.validar(
            _datos_producto_base(
                codigo_barras="7701234567890",
            ),
        )


@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "codigo_automatico_habilitado",
    return_value=False,
)
def test_producto_validar_normaliza_codigo(
    _mock_auto,
    _mock_codigo,
):
    datos = _datos_producto_base(
        codigo=" prd001 ",
    )

    ServicioProducto.validar(
        datos,
    )

    assert datos["codigo"] == "PRD001"


@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "codigo_automatico_habilitado",
    return_value=False,
)
def test_producto_validar_servicio_anula_existencia_y_stock(
    _mock_auto,
    _mock_codigo,
):
    datos = _datos_producto_base(
        tipo="servicio",
        existencia=50,
        stock_minimo=10,
    )

    ServicioProducto.validar(
        datos,
    )

    assert datos["existencia"] == 0.0
    assert datos["stock_minimo"] == 0.0


@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "codigo_automatico_habilitado",
    return_value=False,
)
def test_producto_validar_variantes_anula_existencia_cabecera(
    _mock_auto,
    _mock_codigo,
):
    datos = _datos_producto_base(
        maneja_variantes=True,
        existencia=40,
    )

    ServicioProducto.validar(
        datos,
    )

    assert datos["existencia"] == 0.0


@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "codigo_automatico_habilitado",
    return_value=False,
)
def test_producto_validar_stock_minimo_no_negativo(
    _mock_auto,
    _mock_codigo,
):
    datos = _datos_producto_base(
        stock_minimo=-5,
    )

    ServicioProducto.validar(
        datos,
    )

    assert datos["stock_minimo"] == 0.0


@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "codigo_automatico_habilitado",
    return_value=False,
)
def test_producto_validar_normaliza_impuesto_vacio(
    _mock_auto,
    _mock_codigo,
):
    datos = _datos_producto_base(
        impuesto_compra_id="",
    )

    ServicioProducto.validar(
        datos,
    )

    assert datos["impuesto_compra_id"] is None
    assert datos["impuesto_venta_id"] == 1


def test_producto_validar_variantes_requiere_al_menos_una():
    with pytest.raises(
        ValueError,
        match="variante",
    ):
        ServicioProducto._validar_variantes(
            [],
            "PRD001",
            True,
        )


@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "_codigo_variante_ocupado",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "_codigo_barras_ocupado",
    return_value=False,
)
def test_producto_validar_variantes_nueva_inicia_existencia_cero(
    _mock_barras,
    _mock_variante,
    _mock_codigo,
):
    filas = ServicioProducto._validar_variantes(
        [
            {
                "talla": "M",
                "color": "Azul",
                "existencia": 99,
            },
        ],
        "PRD001",
        True,
    )

    assert filas[0]["existencia"] == 0.0


@patch.object(
    ServicioProducto.repositorio,
    "listar_variantes",
    return_value=[
        SimpleNamespace(
            codigo="PRD001-V01",
            existencia=15.0,
        ),
    ],
)
@patch.object(
    ServicioProducto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "_codigo_variante_ocupado",
    return_value=False,
)
@patch.object(
    ServicioProducto,
    "_codigo_barras_ocupado",
    return_value=False,
)
def test_producto_validar_variantes_preserva_existencia_kardex(
    _mock_barras,
    _mock_variante,
    _mock_codigo,
    _mock_listar,
):
    filas = ServicioProducto._validar_variantes(
        [
            {
                "codigo": "PRD001-V01",
                "talla": "M",
                "color": "Azul",
                "existencia": 999,
            },
        ],
        "PRD001",
        True,
        producto_id=1,
    )

    assert filas[0]["existencia"] == 15.0


def test_producto_definition_existencia_solo_lectura():
    campo = ProductoDefinition.buscar_campo(
        "existencia",
    )

    assert campo is not None
    assert campo.habilitado is False
