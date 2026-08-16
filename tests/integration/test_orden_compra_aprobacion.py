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


def _crear_proveedor(sufijo: str):

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    documento = str(
        900000000
        + int(sufijo[:6], 16) % 99999999,
    )

    return TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": documento,
            "tipo_tercero": "Proveedor",
            "razon_social": f"Proveedor Aprobacion {sufijo}",
            "pais": "Colombia",
            "resp_r99_pn": True,
        },
    )


def _crear_producto(sufijo: str):

    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )

    return ServicioProducto.guardar_completo(
        {
            "codigo": f"APR{sufijo.upper()}",
            "nombre": f"Producto Aprobacion {sufijo}",
            "tipo": "producto",
            "precio_venta": 1000,
            "costo": 500,
            "existencia": 0,
            "stock_minimo": 0,
            "activo": True,
        },
    )


def _crear_bodega(sufijo: str):

    from aplicacion.modulos.inventario.bodegas.servicios import (
        ServicioBodega,
    )

    return ServicioBodega.guardar(
        {
            "codigo": f"BOD{sufijo[:5]}",
            "nombre": f"Bodega Aprobacion {sufijo}",
        },
    )


def _crear_orden(proveedor_id, producto_id, costo_unitario):

    from aplicacion.modulos.compras.ordenes.servicios import (
        ServicioOrdenCompra,
    )

    return ServicioOrdenCompra.guardar(
        proveedor_id=proveedor_id,
        fecha=date.today(),
        lineas=[
            {
                "producto_id": producto_id,
                "descripcion": "Línea de prueba",
                "cantidad": 1,
                "costo_unitario": costo_unitario,
            },
        ],
    )


def _habilitar_umbrales(
    monkeypatch,
    *,
    nivel1: float = 0,
    nivel2: float = 0,
):

    from aplicacion.nucleo.configuracion import Configuracion

    datos = Configuracion.cargar()

    monkeypatch.setitem(
        datos,
        "compras",
        {
            "aprobacion_nivel1_monto": nivel1,
            "aprobacion_nivel2_monto": nivel2,
        },
    )


class TestAprobacionOrdenesCompra:

    def test_orden_bajo_el_umbral_no_requiere_aprobacion(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        _habilitar_umbrales(
            monkeypatch,
            nivel1=1000000,
        )

        sufijo = _sufijo()

        proveedor = _crear_proveedor(sufijo)
        producto = _crear_producto(sufijo)

        orden = _crear_orden(
            proveedor.id,
            producto.id,
            500,
        )

        assert orden.estado_aprobacion == "no_aplica"

    def test_orden_supera_umbral_nivel1_requiere_aprobacion(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        _habilitar_umbrales(
            monkeypatch,
            nivel1=1000,
        )

        sufijo = _sufijo()

        proveedor = _crear_proveedor(sufijo)
        producto = _crear_producto(sufijo)

        orden = _crear_orden(
            proveedor.id,
            producto.id,
            5000,
        )

        assert orden.estado_aprobacion == "pendiente_nivel1"

    def test_aprobar_nivel1_deja_aprobada_sin_nivel2(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        from aplicacion.modulos.compras.ordenes.servicios import (
            ServicioOrdenCompra,
        )

        _habilitar_umbrales(
            monkeypatch,
            nivel1=1000,
        )

        sufijo = _sufijo()

        proveedor = _crear_proveedor(sufijo)
        producto = _crear_producto(sufijo)

        orden = _crear_orden(
            proveedor.id,
            producto.id,
            5000,
        )

        actualizada = ServicioOrdenCompra.aprobar_nivel1(
            orden.id,
            "usuario.prueba",
        )

        assert actualizada.estado_aprobacion == "aprobada"
        assert actualizada.aprobado_nivel1_por == "usuario.prueba"

    def test_aprobar_nivel1_pasa_a_pendiente_nivel2(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        from aplicacion.modulos.compras.ordenes.servicios import (
            ServicioOrdenCompra,
        )

        _habilitar_umbrales(
            monkeypatch,
            nivel1=1000,
            nivel2=4000,
        )

        sufijo = _sufijo()

        proveedor = _crear_proveedor(sufijo)
        producto = _crear_producto(sufijo)

        orden = _crear_orden(
            proveedor.id,
            producto.id,
            5000,
        )

        actualizada = ServicioOrdenCompra.aprobar_nivel1(
            orden.id,
            "usuario.prueba",
        )

        assert (
            actualizada.estado_aprobacion
            == "pendiente_nivel2"
        )

        final = ServicioOrdenCompra.aprobar_nivel2(
            orden.id,
            "gerente.prueba",
        )

        assert final.estado_aprobacion == "aprobada"
        assert final.aprobado_nivel2_por == "gerente.prueba"

    def test_no_permite_aprobar_nivel2_sin_pasar_por_nivel1(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        from aplicacion.modulos.compras.ordenes.servicios import (
            ServicioOrdenCompra,
        )

        _habilitar_umbrales(
            monkeypatch,
            nivel1=1000,
            nivel2=4000,
        )

        sufijo = _sufijo()

        proveedor = _crear_proveedor(sufijo)
        producto = _crear_producto(sufijo)

        orden = _crear_orden(
            proveedor.id,
            producto.id,
            5000,
        )

        with pytest.raises(ValueError):

            ServicioOrdenCompra.aprobar_nivel2(
                orden.id,
                "gerente.prueba",
            )

    def test_rechazar_aprobacion(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        from aplicacion.modulos.compras.ordenes.servicios import (
            ServicioOrdenCompra,
        )

        _habilitar_umbrales(
            monkeypatch,
            nivel1=1000,
        )

        sufijo = _sufijo()

        proveedor = _crear_proveedor(sufijo)
        producto = _crear_producto(sufijo)

        orden = _crear_orden(
            proveedor.id,
            producto.id,
            5000,
        )

        rechazada = ServicioOrdenCompra.rechazar_aprobacion(
            orden.id,
            "usuario.prueba",
            "Presupuesto insuficiente",
        )

        assert rechazada.estado_aprobacion == "rechazada"
        assert "Presupuesto insuficiente" in (
            rechazada.motivo_rechazo
        )

    def test_registrar_recepcion_bloqueada_si_pendiente_aprobacion(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        from aplicacion.modulos.compras.ordenes.servicios import (
            ServicioOrdenCompra,
        )

        _habilitar_umbrales(
            monkeypatch,
            nivel1=1000,
        )

        sufijo = _sufijo()

        proveedor = _crear_proveedor(sufijo)
        producto = _crear_producto(sufijo)
        bodega = _crear_bodega(sufijo)

        orden = _crear_orden(
            proveedor.id,
            producto.id,
            5000,
        )

        orden_completa = ServicioOrdenCompra.obtener_completa(
            orden.id,
        )

        detalle_id = orden_completa.detalles[0].id

        with pytest.raises(
            ValueError,
            match="requiere aprobación",
        ):

            ServicioOrdenCompra.registrar_recepcion(
                orden_id=orden.id,
                bodega_id=bodega.id,
                fecha=date.today(),
                lineas=[
                    {
                        "orden_detalle_id": detalle_id,
                        "producto_id": producto.id,
                        "cantidad": 1,
                        "costo_unitario": 5000,
                    },
                ],
            )

    def test_registrar_recepcion_permitida_tras_aprobar(
        self,
        requiere_postgresql,
        monkeypatch,
    ):

        from aplicacion.modulos.compras.ordenes.servicios import (
            ServicioOrdenCompra,
        )

        _habilitar_umbrales(
            monkeypatch,
            nivel1=1000,
        )

        sufijo = _sufijo()

        proveedor = _crear_proveedor(sufijo)
        producto = _crear_producto(sufijo)
        bodega = _crear_bodega(sufijo)

        orden = _crear_orden(
            proveedor.id,
            producto.id,
            5000,
        )

        ServicioOrdenCompra.aprobar_nivel1(
            orden.id,
            "usuario.prueba",
        )

        orden_completa = ServicioOrdenCompra.obtener_completa(
            orden.id,
        )

        detalle_id = orden_completa.detalles[0].id

        recepcion = ServicioOrdenCompra.registrar_recepcion(
            orden_id=orden.id,
            bodega_id=bodega.id,
            fecha=date.today(),
            lineas=[
                {
                    "orden_detalle_id": detalle_id,
                    "producto_id": producto.id,
                    "cantidad": 1,
                    "costo_unitario": 5000,
                },
            ],
        )

        assert recepcion.id is not None
