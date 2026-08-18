from __future__ import annotations

import os
import uuid
from datetime import date

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


def _documento(sufijo: str) -> str:

    return str(
        900000000
        + int(sufijo[:6], 16) % 99999999,
    )


def _crear_cliente(sufijo: str):

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    return TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": _documento(sufijo),
            "tipo_tercero": "Cliente",
            "razon_social": f"Panel Gerencial Demo {sufijo}",
            "pais": "Colombia",
            "resp_r99_pn": True,
        },
    )


def _crear_producto(sufijo: str):

    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )

    return ServicioProducto.guardar(
        {
            "codigo": f"PG-{sufijo}",
            "nombre": f"Producto Panel Gerencial {sufijo}",
            "precio_venta": 50000,
        },
    )


def _crear_factura_venta_con_detalle(
    cliente_id: int,
    producto_id: int,
    sufijo: str,
    *,
    fecha: date,
    cantidad: float,
    precio_unitario: float,
):

    from aplicacion.base_datos.conexion import SessionLocal
    from aplicacion.modulos.ventas.facturas.modelos import (
        FacturaVenta,
        FacturaVentaDetalle,
    )

    total = cantidad * precio_unitario

    db = SessionLocal()

    try:

        factura = FacturaVenta(
            numero=f"FV-PG-{sufijo}",
            fecha=fecha,
            cliente_id=cliente_id,
            subtotal=total,
            total=total,
            saldo_pendiente=total,
        )

        db.add(factura)
        db.flush()

        db.add(
            FacturaVentaDetalle(
                factura_id=factura.id,
                producto_id=producto_id,
                descripcion="Detalle de prueba",
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                total_linea=total,
            )
        )

        db.commit()
        db.refresh(factura)

        return factura.id

    finally:

        db.close()


class TestTopProductosVendidos:

    def test_agrega_por_producto_dentro_del_periodo(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.gerencial.servicios import (
            ServicioPanelGerencial,
        )

        sufijo = _sufijo()
        cliente = _crear_cliente(sufijo)
        producto = _crear_producto(sufijo)

        hoy = date.today()

        _crear_factura_venta_con_detalle(
            cliente.id,
            producto.id,
            sufijo,
            fecha=hoy,
            cantidad=3,
            precio_unitario=50000,
        )

        top = ServicioPanelGerencial._top_productos_vendidos(
            hoy.replace(day=1),
            hoy,
        )

        fila = next(
            (
                f
                for f in top
                if f["producto_id"] == producto.id
            ),
            None,
        )

        assert fila is not None
        assert fila["cantidad"] == 3
        assert fila["valor"] == 150000.0

    def test_excluye_facturas_fuera_del_periodo(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.gerencial.servicios import (
            ServicioPanelGerencial,
        )

        sufijo = _sufijo()
        cliente = _crear_cliente(sufijo)
        producto = _crear_producto(sufijo)

        fecha_vieja = date(2020, 1, 15)

        _crear_factura_venta_con_detalle(
            cliente.id,
            producto.id,
            sufijo,
            fecha=fecha_vieja,
            cantidad=5,
            precio_unitario=20000,
        )

        hoy = date.today()

        top = ServicioPanelGerencial._top_productos_vendidos(
            hoy.replace(day=1),
            hoy,
        )

        assert all(
            f["producto_id"] != producto.id for f in top
        )

    def test_periodo_sin_ventas_retorna_lista_vacia(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.gerencial.servicios import (
            ServicioPanelGerencial,
        )

        top = ServicioPanelGerencial._top_productos_vendidos(
            date(2001, 1, 1),
            date(2001, 1, 31),
        )

        assert top == []


class TestSerieMensual:

    def test_incluye_mes_actual_con_ventas_y_compras(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.gerencial.servicios import (
            ServicioPanelGerencial,
        )

        sufijo = _sufijo()
        cliente = _crear_cliente(sufijo)
        producto = _crear_producto(sufijo)

        hoy = date.today()

        _crear_factura_venta_con_detalle(
            cliente.id,
            producto.id,
            sufijo,
            fecha=hoy,
            cantidad=2,
            precio_unitario=60000,
        )

        serie = ServicioPanelGerencial._serie_mensual(
            meses=3,
        )

        assert len(serie) == 3

        mes_actual = next(
            p
            for p in serie
            if p["anio"] == hoy.year and p["mes"] == hoy.month
        )

        assert mes_actual["ventas"] >= 120000.0

    def test_retorna_meses_en_orden_cronologico(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.gerencial.servicios import (
            ServicioPanelGerencial,
        )

        serie = ServicioPanelGerencial._serie_mensual(
            meses=4,
        )

        claves = [
            (punto["anio"], punto["mes"]) for punto in serie
        ]

        assert claves == sorted(claves)
