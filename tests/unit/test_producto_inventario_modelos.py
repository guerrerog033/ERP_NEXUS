"""Modelos producto + inventario (Fase 22)."""

from __future__ import annotations

from aplicacion.base_datos.registro_modelos import importar_modelos
from aplicacion.maestros.productos.modelos import (
    Producto,
    ProductoVariante,
)
from aplicacion.maestros.productos.precio_modelo import ProductoPrecio
from aplicacion.modulos.inventario.modelos import (
    Bodega,
    ExistenciaBodega,
    MovimientoInventario,
)


def test_modelos_producto_inventario_registrados():

    importar_modelos()

    assert Producto.__tablename__ == "productos"
    assert ProductoPrecio.__tablename__ == "producto_precios"
    assert ProductoVariante.__tablename__ == "producto_variantes"
    assert Bodega.__tablename__ == "bodegas"
    assert ExistenciaBodega.__tablename__ == "existencias_bodega"
    assert MovimientoInventario.__tablename__ == "movimientos_inventario"


def test_producto_tiene_variantes_property():

    producto = Producto(
        codigo="CAM",
        nombre="Camiseta",
        maneja_variantes=True,
    )

    assert producto.tiene_variantes is True


def test_variante_nombre_completo():

    producto = Producto(
        codigo="CAM",
        nombre="Camiseta básica",
    )

    variante = ProductoVariante(
        producto=producto,
        codigo="CAM-ROJ-M",
        color="Rojo",
        talla="M",
    )

    assert "Camiseta básica" in variante.nombre_completo
    assert "Rojo" in variante.nombre_completo


def test_existencia_bodega_disponible():

    registro = ExistenciaBodega(
        cantidad=100,
        cantidad_reservada=25,
    )

    assert registro.disponible == 75
