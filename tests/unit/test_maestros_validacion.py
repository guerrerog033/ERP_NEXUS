from __future__ import annotations

from unittest.mock import patch

import pytest

from aplicacion.maestros.categorias.categoria_definition import (
    CategoriaDefinition,
)
from aplicacion.maestros.categorias.categorias_table import (
    CategoriaTable,
)
from aplicacion.maestros.categorias.servicios import (
    ServicioCategoria,
)
from aplicacion.maestros.empresas.empresa_definition import (
    EmpresaDefinition,
)
from aplicacion.maestros.empresas.empresas_table import (
    EmpresaTable,
)
from aplicacion.maestros.empresas.servicios import (
    EmpresaServicio,
)
from aplicacion.maestros.impuestos.impuesto_definition import (
    ImpuestoDefinition,
)
from aplicacion.maestros.impuestos.impuestos_table import (
    ImpuestoTable,
)
from aplicacion.maestros.impuestos.servicios import (
    ServicioImpuesto,
)
from aplicacion.maestros.listas_precio.lista_precio_definition import (
    ListaPrecioDefinition,
)
from aplicacion.maestros.listas_precio.listas_precio_table import (
    ListaPrecioTable,
)
from aplicacion.maestros.listas_precio.servicios import (
    ServicioListaPrecio,
)
from aplicacion.maestros.marcas.marca_definition import (
    MarcaDefinition,
)
from aplicacion.maestros.marcas.marcas_table import (
    MarcaTable,
)
from aplicacion.maestros.marcas.servicios import (
    ServicioMarca,
)
from aplicacion.maestros.productos.producto_definition import (
    ProductoDefinition,
)
from aplicacion.maestros.productos.productos_table import (
    ProductoTable,
)
from aplicacion.maestros.terceros.terceros_definition import (
    TerceroDefinition,
)
from aplicacion.maestros.terceros.terceros_table import (
    TerceroTable,
)


def test_definiciones_tabla_maestros():
    assert CategoriaDefinition.table_definition is CategoriaTable
    assert MarcaDefinition.table_definition is MarcaTable
    assert ProductoDefinition.table_definition is ProductoTable
    assert TerceroDefinition.table_definition is TerceroTable
    assert ImpuestoDefinition.table_definition is ImpuestoTable
    assert ListaPrecioDefinition.table_definition is ListaPrecioTable
    assert EmpresaDefinition.table_definition is EmpresaTable
    assert len(
        ProductoTable.columnas,
    ) >= 8


@pytest.mark.parametrize(
    "servicio,datos,mensaje",
    [
        (
            ServicioMarca,
            {
                "codigo": "",
                "nombre": "Marca",
            },
            "código",
        ),
        (
            ServicioCategoria,
            {
                "codigo": "",
                "nombre": "Categoría",
            },
            "código",
        ),
        (
            ServicioImpuesto,
            {
                "codigo": "",
                "nombre": "IVA",
            },
            "código",
        ),
        (
            ServicioListaPrecio,
            {
                "codigo": "",
                "nombre": "Lista",
            },
            "código",
        ),
    ],
)
@patch.object(
    ServicioMarca.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioCategoria.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioImpuesto.repositorio,
    "existe_codigo",
    return_value=False,
)
@patch.object(
    ServicioListaPrecio.repositorio,
    "existe_codigo",
    return_value=False,
)
def test_maestro_validar_requiere_codigo(
    _mock_lista,
    _mock_impuesto,
    _mock_categoria,
    _mock_marca,
    servicio,
    datos,
    mensaje,
):
    with pytest.raises(
        ValueError,
        match=mensaje,
    ):
        servicio.validar(
            dict(
                datos,
            ),
        )


@patch.object(
    ServicioMarca.repositorio,
    "existe_codigo",
    return_value=False,
)
def test_marca_validar_requiere_nombre(
    _mock_existe,
):
    with pytest.raises(
        ValueError,
        match="nombre",
    ):
        ServicioMarca.validar(
            {
                "codigo": "M01",
                "nombre": "",
            },
        )


@patch.object(
    ServicioMarca.repositorio,
    "existe_codigo",
    return_value=False,
)
def test_marca_validar_normaliza_codigo(
    _mock_existe,
):
    datos = {
        "codigo": " m01 ",
        "nombre": "Marca",
    }

    ServicioMarca.validar(
        datos,
    )

    assert datos["codigo"] == "M01"


@patch.object(
    ServicioCategoria.repositorio,
    "existe_codigo",
    return_value=False,
)
def test_categoria_validar_requiere_nombre(
    _mock_existe,
):
    with pytest.raises(
        ValueError,
        match="nombre",
    ):
        ServicioCategoria.validar(
            {
                "codigo": "CAT01",
                "nombre": "",
            },
        )


@patch.object(
    ServicioImpuesto.repositorio,
    "existe_codigo",
    return_value=True,
)
def test_impuesto_validar_rechaza_codigo_duplicado(
    _mock_existe,
):
    with pytest.raises(
        ValueError,
        match="código",
    ):
        ServicioImpuesto.validar(
            {
                "codigo": "IVA19",
                "nombre": "IVA 19%",
            },
        )


@patch.object(
    ServicioImpuesto.repositorio,
    "existe_codigo",
    return_value=False,
)
def test_impuesto_validar_normaliza_porcentaje(
    _mock_existe,
):
    datos = {
        "codigo": "IVA5",
        "nombre": "IVA 5%",
        "porcentaje": "5",
        "tipo": "IVA",
    }

    ServicioImpuesto.validar(
        datos,
    )

    assert datos["porcentaje"] == 5.0
    assert datos["tipo"] == "IVA"


@patch.object(
    ServicioListaPrecio.repositorio,
    "existe_codigo",
    return_value=False,
)
def test_lista_precio_validar_normaliza_predeterminada(
    _mock_existe,
):
    datos = {
        "codigo": "LP01",
        "nombre": "General",
        "predeterminada": 1,
    }

    ServicioListaPrecio.validar(
        datos,
    )

    assert datos["predeterminada"] is True


@patch.object(
    EmpresaServicio.repositorio,
    "obtener_por_nit",
    return_value=None,
)
def test_empresa_validar_requiere_nit(
    _mock_nit,
):
    with pytest.raises(
        Exception,
        match="NIT",
    ):
        EmpresaServicio.validar(
            {
                "nit": "",
                "razon_social": "Empresa Demo",
            },
        )


@patch.object(
    EmpresaServicio.repositorio,
    "obtener_por_nit",
    return_value=None,
)
def test_empresa_validar_requiere_razon_social(
    _mock_nit,
):
    with pytest.raises(
        Exception,
        match="razón social",
    ):
        EmpresaServicio.validar(
            {
                "nit": "900123456",
                "razon_social": "",
            },
        )
