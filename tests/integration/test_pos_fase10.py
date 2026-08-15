from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import inspect

from aplicacion.base_datos.conexion import engine
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


@pytest.fixture
def sufijo_unico():
    return uuid.uuid4().hex[:8]


def test_tablas_fase10_existen(
    requiere_postgresql,
):

    inspector = inspect(
        engine,
    )

    tablas = set(
        inspector.get_table_names(),
    )

    assert "pos_ventas_log" in tablas
    assert "pos_cierres_caja" in tablas

    columnas = {
        col["name"]
        for col in inspector.get_columns(
            "productos",
        )
    }

    assert "stock_minimo" in columnas


def test_resumen_caja_dia_sin_ventas(
    requiere_postgresql,
):

    from datetime import date

    from aplicacion.modulos.ventas.pos.servicios import (
        ServicioPOSVenta,
    )

    resumen = ServicioPOSVenta.resumen_caja(
        fecha=date(
            2099,
            12,
            31,
        ),
    )

    assert resumen["ventas"] == 0
    assert resumen["total"] == 0.0


def test_efectivo_esperado_dia_sin_ventas(
    requiere_postgresql,
):

    from datetime import date

    from aplicacion.modulos.ventas.pos.servicios import (
        ServicioPOSVenta,
    )

    esperado = ServicioPOSVenta.efectivo_esperado(
        fecha=date(
            2099,
            12,
            31,
        ),
    )

    assert esperado == 0.0


def test_cerrar_caja_registra_arqueo(
    requiere_postgresql,
    sufijo_unico,
):

    from datetime import date

    from aplicacion.modulos.ventas.pos.servicios import (
        ServicioPOSVenta,
    )

    dia = date(
        2099,
        1,
        1
        + int(
            sufijo_unico[:2],
            16,
        )
        % 28,
    )

    cierre = ServicioPOSVenta.cerrar_caja(
        efectivo_contado=0.0,
        fecha=dia,
        observaciones="E2E arqueo",
    )

    assert cierre["diferencia"] == 0.0

    existente = ServicioPOSVenta.obtener_cierre(
        fecha=dia,
    )

    assert existente is not None
    assert existente["observaciones"] == "E2E arqueo"


def _preparar_maestros_pos():
    from aplicacion.maestros.impuestos.iva_catalogo import (
        id_iva_predeterminado,
    )
    from aplicacion.maestros.impuestos.servicios import (
        ServicioImpuesto,
    )
    from aplicacion.maestros.listas_precio.servicios import (
        ServicioListaPrecio,
    )

    ServicioImpuesto.inicializar_predeterminados()
    ServicioListaPrecio.inicializar_predeterminados()

    impuesto_id = id_iva_predeterminado()

    if impuesto_id is None:

        pytest.fail(
            "No hay IVA predeterminado en la base de datos.",
        )

    return impuesto_id


def _datos_cliente_pos(
    sufijo: str,
) -> dict:
    documento = str(
        900000000
        + int(
            sufijo[:6],
            16,
        )
        % 100000000,
    )

    return {
        "tipo_documento": "NIT",
        "numero_documento": documento,
        "tipo_tercero": "Cliente",
        "razon_social": f"Cliente POS Demo {sufijo}",
        "nombre_comercial": f"Cliente POS {sufijo}",
        "direccion": "Calle POS # 1-1",
        "pais": "Colombia",
        "departamento": "Cundinamarca",
        "ciudad": "Bogotá",
        "correo": f"pos.{sufijo}@demo.com",
        "telefono": "6017654321",
        "dias_credito": 0,
        "cupo_credito": 1000000,
        "resp_r99_pn": True,
        "activo": True,
    }


def _datos_producto_pos(
    sufijo: str,
    impuesto_id: int,
) -> dict:
    return {
        "codigo": f"POS{sufijo.upper()}",
        "nombre": f"Producto POS Demo {sufijo}",
        "tipo": "producto",
        "unidad_medida": "Und",
        "precio_venta": 25000,
        "precio_incluye_iva": False,
        "costo": 12000,
        "existencia": 100,
        "stock_minimo": 5,
        "impuesto_venta_id": impuesto_id,
        "impuesto_compra_id": None,
        "activo": True,
        "maneja_variantes": False,
    }


def _abastecer_inventario_pos(
    producto_id: int,
    cantidad: float = 100,
) -> None:
    from datetime import date

    from aplicacion.base_datos.conexion import (
        SessionLocal,
    )
    from aplicacion.maestros.productos.modelos import (
        Producto,
    )
    from aplicacion.modulos.inventario.servicios import (
        ServicioInventario,
    )

    bodega = ServicioInventario.inicializar_bodega()
    db = SessionLocal()

    try:

        producto = (
            db.query(Producto)
            .filter(
                Producto.id == producto_id,
            )
            .first()
        )

        if producto is None:

            pytest.fail(
                "Producto no encontrado para abastecer inventario POS.",
            )

        ServicioInventario.registrar_entrada(
            db,
            bodega_id=bodega.id,
            producto=producto,
            producto_variante_id=None,
            cantidad=cantidad,
            costo_unitario=float(
                producto.costo or 0,
            ),
            referencia="test_pos_setup",
            referencia_id=producto_id,
            fecha=date.today(),
            observaciones="Setup integración POS",
        )

        db.commit()

    finally:

        db.close()


def _disponible_pos(
    producto_id: int,
) -> float:
    from aplicacion.base_datos.conexion import (
        SessionLocal,
    )
    from aplicacion.modulos.inventario.servicios import (
        ServicioInventario,
    )

    bodega = ServicioInventario.inicializar_bodega()
    db = SessionLocal()

    try:

        return ServicioInventario._disponible_bodega(
            db,
            bodega_id=bodega.id,
            producto_id=producto_id,
            producto_variante_id=None,
        )

    finally:

        db.close()


def test_pos_facturar_registra_venta_inventario_y_log(
    requiere_postgresql,
    sufijo_unico,
):
    from datetime import date

    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.pos.servicios import (
        ServicioPOSVenta,
    )

    impuesto_id = _preparar_maestros_pos()
    sufijo = f"{sufijo_unico}pos"

    cliente = TerceroServicio.guardar(
        _datos_cliente_pos(
            sufijo,
        ),
    )

    producto = ServicioProducto.guardar_completo(
        _datos_producto_pos(
            sufijo,
            impuesto_id,
        ),
    )

    _abastecer_inventario_pos(
        producto.id,
    )

    stock_inicial = _disponible_pos(
        producto.id,
    )

    ventas_antes = ServicioPOSVenta.resumen_caja(
        fecha=date.today(),
    )["ventas"]

    factura = ServicioPOSVenta.facturar(
        cliente_id=cliente.id,
        lineas=[
            {
                "producto_id": producto.id,
                "descripcion": producto.nombre,
                "cantidad": 1,
                "precio_unitario": 25000,
                "impuesto_id": impuesto_id,
                "precio_incluye_iva": False,
            },
        ],
        recibido=50000,
        cambio=20250,
        metodo_pago="efectivo",
    )

    assert factura.estado in (
        "generada",
        "contabilizada",
    )
    assert factura.inventario_aplicado is True
    assert float(
        factura.total or 0,
    ) > 0

    stock_final = _disponible_pos(
        producto.id,
    )

    assert stock_final == stock_inicial - 1

    resumen = ServicioPOSVenta.resumen_caja(
        fecha=date.today(),
    )

    assert resumen["ventas"] == ventas_antes + 1
    assert float(
        resumen["total"],
    ) >= float(
        factura.total or 0,
    )

    historial = ServicioPOSVenta.listar_historial(
        limite=20,
    )

    assert any(
        item["factura_numero"] == factura.numero
        for item in historial
    )

    assert ServicioPOSVenta.efectivo_esperado(
        fecha=date.today(),
    ) >= float(
        factura.total or 0,
    )


def test_pos_tarjeta_no_suma_efectivo_esperado(
    requiere_postgresql,
    sufijo_unico,
):
    from datetime import date

    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.pos.servicios import (
        ServicioPOSVenta,
    )

    impuesto_id = _preparar_maestros_pos()
    sufijo = f"{sufijo_unico}tar"

    cliente = TerceroServicio.guardar(
        _datos_cliente_pos(
            sufijo,
        ),
    )

    producto = ServicioProducto.guardar_completo(
        _datos_producto_pos(
            sufijo,
            impuesto_id,
        ),
    )

    _abastecer_inventario_pos(
        producto.id,
    )

    esperado_antes = ServicioPOSVenta.efectivo_esperado(
        fecha=date.today(),
    )

    factura = ServicioPOSVenta.facturar(
        cliente_id=cliente.id,
        lineas=[
            {
                "producto_id": producto.id,
                "descripcion": producto.nombre,
                "cantidad": 1,
                "precio_unitario": 25000,
                "impuesto_id": impuesto_id,
                "precio_incluye_iva": False,
            },
        ],
        metodo_pago="tarjeta",
        recibido=29750,
        cambio=0,
    )

    assert float(
        factura.total or 0,
    ) > 0

    esperado_despues = ServicioPOSVenta.efectivo_esperado(
        fecha=date.today(),
    )

    assert esperado_despues == pytest.approx(
        esperado_antes,
        rel=0,
        abs=0.02,
    )

    resumen = ServicioPOSVenta.resumen_caja(
        fecha=date.today(),
    )

    tarjeta = next(
        (
            item
            for item in resumen["por_metodo"]
            if item["metodo_pago"] == "tarjeta"
        ),
        None,
    )

    assert tarjeta is not None
    assert tarjeta["ventas"] >= 1


def test_pos_devolucion_nota_credito_revierte_saldo_e_inventario(
    requiere_postgresql,
    sufijo_unico,
):
    from datetime import date

    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )
    from aplicacion.modulos.ventas.pos.servicios import (
        ServicioPOSVenta,
    )

    impuesto_id = _preparar_maestros_pos()
    sufijo = f"{sufijo_unico}dev"

    cliente = TerceroServicio.guardar(
        _datos_cliente_pos(
            sufijo,
        ),
    )

    producto = ServicioProducto.guardar_completo(
        _datos_producto_pos(
            sufijo,
            impuesto_id,
        ),
    )

    _abastecer_inventario_pos(
        producto.id,
    )

    stock_inicial = _disponible_pos(
        producto.id,
    )

    factura = ServicioPOSVenta.facturar(
        cliente_id=cliente.id,
        lineas=[
            {
                "producto_id": producto.id,
                "descripcion": producto.nombre,
                "cantidad": 1,
                "precio_unitario": 25000,
                "impuesto_id": impuesto_id,
                "precio_incluye_iva": False,
            },
        ],
        metodo_pago="efectivo",
    )

    stock_tras_venta = _disponible_pos(
        producto.id,
    )

    assert stock_tras_venta == stock_inicial - 1

    saldo_inicial = float(
        factura.saldo_pendiente or 0,
    )

    assert saldo_inicial > 0

    nota = ServicioPOSVenta.devolver_venta(
        factura_id=factura.id,
        motivo="Devolución POS integración",
    )

    assert nota.factura_id == factura.id
    assert nota.contabilizado is True

    factura_actualizada = ServicioFacturaVenta.obtener_completa(
        factura.id,
    )

    assert float(
        factura_actualizada.saldo_pendiente or 0,
    ) < saldo_inicial

    stock_final = _disponible_pos(
        producto.id,
    )

    assert stock_final == stock_inicial

    historial = ServicioPOSVenta.listar_historial(
        fecha_desde=date.today(),
        fecha_hasta=date.today(),
        limite=50,
    )

    assert any(
        item["factura_numero"] == factura.numero
        for item in historial
    )


def test_pos_cierre_con_diferencia_arqueo(
    requiere_postgresql,
    sufijo_unico,
):
    from datetime import date

    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.pos.servicios import (
        ServicioPOSVenta,
    )

    hoy = date.today()

    if ServicioPOSVenta.obtener_cierre(
        fecha=hoy,
    ) is not None:

        pytest.skip(
            "Caja de hoy ya cerrada",
        )

    impuesto_id = _preparar_maestros_pos()
    sufijo = f"{sufijo_unico}cierre"

    cliente = TerceroServicio.guardar(
        _datos_cliente_pos(
            sufijo,
        ),
    )

    producto = ServicioProducto.guardar_completo(
        _datos_producto_pos(
            sufijo,
            impuesto_id,
        ),
    )

    _abastecer_inventario_pos(
        producto.id,
    )

    # La venta queda registrada hoy; validamos cierre sobre totales actuales.
    factura = ServicioPOSVenta.facturar(
        cliente_id=cliente.id,
        lineas=[
            {
                "producto_id": producto.id,
                "descripcion": producto.nombre,
                "cantidad": 1,
                "precio_unitario": 25000,
                "impuesto_id": impuesto_id,
                "precio_incluye_iva": False,
            },
        ],
        recibido=50000,
        metodo_pago="efectivo",
    )

    esperado = ServicioPOSVenta.efectivo_esperado(
        fecha=hoy,
    )

    assert esperado >= float(
        factura.total or 0,
    )

    sobrante = 1500.0

    cierre = ServicioPOSVenta.cerrar_caja(
        efectivo_contado=esperado + sobrante,
        fecha=hoy,
        observaciones="Arqueo con sobrante demo",
    )

    assert cierre["diferencia"] == pytest.approx(
        sobrante,
        rel=0,
        abs=0.02,
    )
    assert cierre["ventas_count"] >= 1
    assert float(
        cierre["total_ventas"],
    ) >= float(
        factura.total or 0,
    )
