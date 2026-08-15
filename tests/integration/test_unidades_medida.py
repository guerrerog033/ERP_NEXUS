from __future__ import annotations

import os
import uuid

import pytest

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
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


def test_inicializar_predeterminados_siembra_las_siete_unidades(
    requiere_postgresql,
):
    from aplicacion.maestros.unidades_medida.servicios import (
        ServicioUnidadMedida,
        UNIDADES_PREDETERMINADAS,
    )

    ServicioUnidadMedida.inicializar_predeterminados()

    for codigo, _nombre, codigo_dian in UNIDADES_PREDETERMINADAS:

        unidad = ServicioUnidadMedida.repositorio.obtener_por_codigo(
            codigo,
        )

        assert unidad is not None
        assert unidad.codigo_dian == codigo_dian


def test_inicializar_predeterminados_es_idempotente(
    requiere_postgresql,
):
    from aplicacion.maestros.unidades_medida.servicios import (
        ServicioUnidadMedida,
    )

    ServicioUnidadMedida.inicializar_predeterminados()
    total_antes = ServicioUnidadMedida.repositorio.contar()

    ServicioUnidadMedida.inicializar_predeterminados()
    total_despues = ServicioUnidadMedida.repositorio.contar()

    assert total_antes == total_despues


def test_validar_rechaza_codigo_duplicado(
    requiere_postgresql,
):
    from aplicacion.maestros.unidades_medida.servicios import (
        ServicioUnidadMedida,
    )

    codigo = f"U{uuid.uuid4().hex[:5].upper()}"

    ServicioUnidadMedida.guardar(
        {
            "codigo": codigo,
            "nombre": "Unidad de prueba",
        },
    )

    with pytest.raises(
        ValueError,
        match="Ya existe",
    ):

        ServicioUnidadMedida.validar(
            {
                "codigo": codigo,
                "nombre": "Otra",
            },
        )


def test_producto_guardado_sin_unidad_usa_und_por_defecto(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )
    from aplicacion.maestros.unidades_medida.servicios import (
        ServicioUnidadMedida,
    )

    ServicioUnidadMedida.inicializar_predeterminados()

    sufijo = uuid.uuid4().hex[:8]

    producto = ServicioProducto.guardar_completo(
        {
            "codigo": f"UNI{sufijo.upper()}",
            "nombre": f"Producto Unidad Demo {sufijo}",
            "tipo": "producto",
            "precio_venta": 1000,
            "precio_incluye_iva": False,
            "costo": 500,
            "existencia": 0,
            "stock_minimo": 0,
            "activo": True,
            "maneja_variantes": False,
        },
    )

    assert producto.unidad_medida_id is not None
    assert producto.unidad_medida_codigo == "Und"

    unidad = ServicioUnidadMedida.repositorio.obtener_por_id(
        producto.unidad_medida_id,
    )

    assert unidad.codigo_dian == "94"


def test_producto_guardado_con_unidad_explicita(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )
    from aplicacion.maestros.unidades_medida.servicios import (
        ServicioUnidadMedida,
    )

    ServicioUnidadMedida.inicializar_predeterminados()

    litro = ServicioUnidadMedida.repositorio.obtener_por_codigo(
        "Lts",
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = ServicioProducto.guardar_completo(
        {
            "codigo": f"LTS{sufijo.upper()}",
            "nombre": f"Producto Litro Demo {sufijo}",
            "tipo": "producto",
            "unidad_medida_id": litro.id,
            "precio_venta": 3000,
            "precio_incluye_iva": False,
            "costo": 1500,
            "existencia": 0,
            "stock_minimo": 0,
            "activo": True,
            "maneja_variantes": False,
        },
    )

    assert producto.unidad_medida_codigo == "Lts"
    assert producto.unidad_medida_id == litro.id


def test_producto_rechaza_unidad_medida_id_inexistente(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )

    with pytest.raises(
        ValueError,
        match="unidad de medida",
    ):

        ServicioProducto.validar(
            {
                "codigo": "XXX",
                "nombre": "Producto inválido",
                "tipo": "producto",
                "unidad_medida_id": 999999,
                "precio_venta": 0,
                "costo": 0,
                "existencia": 0,
                "stock_minimo": 0,
                "impuesto_venta_id": None,
                "impuesto_compra_id": None,
                "maneja_variantes": False,
            },
        )


def test_codigo_unidad_dian_usa_la_unidad_real_de_un_producto_persistido(
    requiere_postgresql,
):
    """
    Cierra el ciclo completo: un producto real guardado en la BD
    con una unidad de medida real, consultado tal como lo haría
    GeneradorXmlFactura al armar una línea de factura — no un
    doble en memoria, la fila y la sesión (cerrada) son reales.
    """

    from aplicacion.integraciones.dian.generador_xml import (
        GeneradorXmlFactura,
    )
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )
    from aplicacion.maestros.unidades_medida.servicios import (
        ServicioUnidadMedida,
    )

    ServicioUnidadMedida.inicializar_predeterminados()

    galon = ServicioUnidadMedida.repositorio.obtener_por_codigo(
        "Gls",
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = ServicioProducto.guardar_completo(
        {
            "codigo": f"GAL{sufijo.upper()}",
            "nombre": f"Producto Galón Demo {sufijo}",
            "tipo": "producto",
            "unidad_medida_id": galon.id,
            "precio_venta": 5000,
            "precio_incluye_iva": False,
            "costo": 2500,
            "existencia": 0,
            "stock_minimo": 0,
            "activo": True,
            "maneja_variantes": False,
        },
    )

    assert (
        GeneradorXmlFactura._codigo_unidad(
            producto.id,
        )
        == "GLL"
    )
