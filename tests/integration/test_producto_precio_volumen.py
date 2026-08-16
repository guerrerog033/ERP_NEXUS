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


def _sufijo() -> str:

    return uuid.uuid4().hex[:8]


def _crear_producto(sufijo: str, precio_venta: float = 10000):

    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )

    return ServicioProducto.guardar(
        {
            "codigo": f"VOL-{sufijo}",
            "nombre": f"Producto Volumen {sufijo}",
            "precio_venta": precio_venta,
        },
    )


class TestPrecioParaCantidad:

    def test_sin_escalones_no_altera_el_precio(
        self,
        requiere_postgresql,
    ):

        from aplicacion.maestros.productos.precio_volumen_servicio import (
            ServicioPrecioVolumenProducto,
        )

        sufijo = _sufijo()
        producto = _crear_producto(sufijo)

        precio = ServicioPrecioVolumenProducto.precio_para_cantidad(
            producto.id,
            50,
            precio_base=10000,
        )

        assert precio is None

    def test_resuelve_el_escalon_correcto_segun_la_cantidad(
        self,
        requiere_postgresql,
    ):

        from aplicacion.maestros.productos.precio_volumen_servicio import (
            ServicioPrecioVolumenProducto,
        )

        sufijo = _sufijo()
        producto = _crear_producto(sufijo, precio_venta=10000)

        ServicioPrecioVolumenProducto.guardar(
            {
                "producto_id": producto.id,
                "cantidad_minima": 10,
                "precio": 9000,
            },
        )

        ServicioPrecioVolumenProducto.guardar(
            {
                "producto_id": producto.id,
                "cantidad_minima": 50,
                "precio": 8000,
            },
        )

        # Por debajo del primer escalón: precio base del producto.
        assert (
            ServicioPrecioVolumenProducto.precio_para_cantidad(
                producto.id,
                5,
                precio_base=10000,
            )
            == 10000.0
        )

        # Dentro del primer escalón.
        assert (
            ServicioPrecioVolumenProducto.precio_para_cantidad(
                producto.id,
                10,
                precio_base=10000,
            )
            == 9000.0
        )

        assert (
            ServicioPrecioVolumenProducto.precio_para_cantidad(
                producto.id,
                49,
                precio_base=10000,
            )
            == 9000.0
        )

        # Segundo escalón.
        assert (
            ServicioPrecioVolumenProducto.precio_para_cantidad(
                producto.id,
                100,
                precio_base=10000,
            )
            == 8000.0
        )

    def test_listar_ordena_por_cantidad_minima(
        self,
        requiere_postgresql,
    ):

        from aplicacion.maestros.productos.precio_volumen_servicio import (
            ServicioPrecioVolumenProducto,
        )

        sufijo = _sufijo()
        producto = _crear_producto(sufijo)

        ServicioPrecioVolumenProducto.guardar(
            {
                "producto_id": producto.id,
                "cantidad_minima": 100,
                "precio": 7000,
            },
        )

        ServicioPrecioVolumenProducto.guardar(
            {
                "producto_id": producto.id,
                "cantidad_minima": 10,
                "precio": 9000,
            },
        )

        escalones = ServicioPrecioVolumenProducto.listar(
            producto.id,
        )

        cantidades = [
            float(escalon.cantidad_minima)
            for escalon in escalones
        ]

        assert cantidades == sorted(cantidades)
