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


@pytest.fixture
def sufijo_unico():
    return uuid.uuid4().hex[:8]


def _datos_cliente(
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
        "razon_social": f"Cliente Flujo Demo {sufijo}",
        "nombre_comercial": f"Cliente Demo {sufijo}",
        "direccion": "Calle 100 # 10-20",
        "pais": "Colombia",
        "departamento": "Cundinamarca",
        "ciudad": "Bogotá",
        "correo": f"cliente.{sufijo}@demo.com",
        "telefono": "6011234567",
        "dias_credito": 30,
        "cupo_credito": 5000000,
        "resp_r99_pn": True,
        "activo": True,
    }


def _datos_producto(
    sufijo: str,
    impuesto_id: int,
) -> dict:
    return {
        "codigo": f"PRD{sufijo.upper()}",
        "nombre": f"Producto Flujo Demo {sufijo}",
        "tipo": "producto",
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


def _preparar_maestros():
    from aplicacion.maestros.empresas.repositorio import (
        EmpresaRepositorio,
    )
    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )
    from aplicacion.maestros.impuestos.iva_catalogo import (
        id_iva_predeterminado,
    )
    from aplicacion.maestros.impuestos.servicios import (
        ServicioImpuesto,
    )
    from aplicacion.maestros.listas_precio.servicios import (
        ServicioListaPrecio,
    )
    from aplicacion.maestros.unidades_medida.servicios import (
        ServicioUnidadMedida,
    )

    if EmpresaRepositorio.obtener_por_nit("900123456") is None:

        EmpresaServicio.guardar(
            {
                "razon_social": "Empresa Demo S.A.S.",
                "nit": "900123456",
                "dv": "7",
                "pais": "Colombia",
                "activo": True,
            },
        )

    ServicioImpuesto.inicializar_predeterminados()
    ServicioListaPrecio.inicializar_predeterminados()
    ServicioUnidadMedida.inicializar_predeterminados()

    impuesto_id = id_iva_predeterminado()

    if impuesto_id is None:

        pytest.fail(
            "No hay IVA predeterminado en la base de datos.",
        )

    return impuesto_id


def _abastecer_inventario(
    producto_id: int,
    cantidad: float = 100,
) -> None:
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
                "Producto no encontrado para abastecer inventario.",
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
            referencia="test_setup",
            referencia_id=producto_id,
            fecha=date.today(),
            observaciones="Setup integración flujo venta",
        )

        db.commit()

    finally:

        db.close()


def _crear_cotizacion_demo(
    *,
    sufijo: str,
    impuesto_id: int,
):
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.cotizaciones.servicios import (
        ServicioCotizacion,
    )

    cliente = TerceroServicio.guardar(
        _datos_cliente(
            sufijo,
        ),
    )

    producto = ServicioProducto.guardar_completo(
        _datos_producto(
            sufijo,
            impuesto_id,
        ),
    )

    _abastecer_inventario(
        producto.id,
    )

    cotizacion = ServicioCotizacion.guardar_completa(
        {
            "cliente_id": cliente.id,
            "fecha": date.today(),
            "estado": "borrador",
            "activo": True,
        },
        [
            {
                "producto_id": producto.id,
                "descripcion": producto.nombre,
                "cantidad": 1,
                "precio_unitario": 25000,
                "impuesto_id": impuesto_id,
                "precio_incluye_iva": False,
            },
        ],
    )

    return cliente, producto, cotizacion


def _nota_credito_parcial_desde_factura(
    factura_id: int,
    *,
    motivo: str,
    factor: float = 0.5,
):
    from aplicacion.modulos.ventas.notas_credito.servicios import (
        ServicioNotaCreditoVenta,
    )

    nota = ServicioNotaCreditoVenta.crear_desde_factura(
        factura_id,
        motivo=motivo,
    )

    nota_completa = ServicioNotaCreditoVenta.obtener_completa(
        nota.id,
    )

    lineas = [
        {
            "producto_id": detalle.producto_id,
            "producto_variante_id": detalle.producto_variante_id,
            "descripcion": detalle.descripcion,
            "cantidad": round(
                float(
                    detalle.cantidad,
                )
                * factor,
                4,
            ),
            "precio_unitario": float(
                detalle.precio_unitario,
            ),
            "impuesto_id": detalle.impuesto_id,
            "precio_incluye_iva": bool(
                detalle.precio_incluye_iva,
            ),
        }
        for detalle in nota_completa.detalles
    ]

    cabecera = {
        "numero": nota_completa.numero,
        "prefijo": nota_completa.prefijo,
        "consecutivo_dian": nota_completa.consecutivo_dian,
        "fecha": nota_completa.fecha,
        "cliente_id": nota_completa.cliente_id,
        "factura_id": nota_completa.factura_id,
        "motivo": nota_completa.motivo,
        "factura_cufe": nota_completa.factura_cufe,
        "retefuente_id": getattr(
            nota_completa,
            "retefuente_id",
            None,
        ),
        "reteica_id": getattr(
            nota_completa,
            "reteica_id",
            None,
        ),
        "reteiva_id": getattr(
            nota_completa,
            "reteiva_id",
            None,
        ),
        "observaciones": nota_completa.observaciones,
        "estado": "borrador",
        "activo": True,
    }

    return ServicioNotaCreditoVenta.guardar_completa(
        cabecera,
        lineas,
        nota.id,
    )


def _disponible_en_bodega(
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


def _contar_movimientos_inventario(
    referencia: str,
    referencia_id: int,
) -> int:
    from aplicacion.base_datos.conexion import (
        SessionLocal,
    )
    from aplicacion.modulos.inventario.modelos import (
        MovimientoInventario,
    )

    db = SessionLocal()

    try:

        return (
            db.query(
                MovimientoInventario,
            )
            .filter(
                MovimientoInventario.referencia
                == referencia,
                MovimientoInventario.referencia_id
                == referencia_id,
            )
            .count()
        )

    finally:

        db.close()


def _confirmar_cotizacion_demo(
    cotizacion_id: int,
):
    from aplicacion.modulos.ventas.cotizaciones.integracion import (
        IntegracionCotizacion,
    )

    return IntegracionCotizacion.confirmar_cotizacion(
        cotizacion_id,
    )


def _confirmar_factura_demo(
    cotizacion_id: int,
):
    from aplicacion.modulos.ventas.facturas.integracion import (
        IntegracionFacturaVenta,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )

    _confirmar_cotizacion_demo(
        cotizacion_id,
    )

    factura = ServicioFacturaVenta.crear_desde_cotizacion(
        cotizacion_id,
    )

    return IntegracionFacturaVenta.confirmar_venta(
        factura.id,
        emitir_dian=False,
    )


def _confirmar_pedido_demo(
    pedido_id: int,
):
    from aplicacion.modulos.ventas.pedidos.integracion import (
        IntegracionPedido,
    )

    return IntegracionPedido.confirmar_pedido(
        pedido_id,
    )


def _confirmar_remision_demo(
    remision_id: int,
):
    from aplicacion.modulos.ventas.remisiones.integracion import (
        IntegracionRemision,
    )

    return IntegracionRemision.confirmar_remision(
        remision_id,
    )


def test_flujo_venta_cotizacion_a_factura(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.cotizaciones.servicios import (
        ServicioCotizacion,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )

    impuesto_id = _preparar_maestros()

    cliente = TerceroServicio.guardar(
        _datos_cliente(
            sufijo_unico,
        ),
    )

    producto = ServicioProducto.guardar_completo(
        _datos_producto(
            sufijo_unico,
            impuesto_id,
        ),
    )

    cotizacion = ServicioCotizacion.guardar_completa(
        {
            "cliente_id": cliente.id,
            "fecha": date.today(),
            "estado": "borrador",
            "activo": True,
            "observaciones": "Flujo demo integración",
        },
        [
            {
                "producto_id": producto.id,
                "descripcion": producto.nombre,
                "cantidad": 2,
                "precio_unitario": 25000,
                "impuesto_id": impuesto_id,
                "precio_incluye_iva": False,
            },
        ],
    )

    assert cotizacion.cliente_id == cliente.id
    assert cotizacion.total > 0

    _confirmar_cotizacion_demo(
        cotizacion.id,
    )

    factura = ServicioFacturaVenta.crear_desde_cotizacion(
        cotizacion.id,
    )

    assert factura.cotizacion_id == cotizacion.id
    assert factura.cliente_id == cliente.id

    factura_completa = ServicioFacturaVenta.obtener_completa(
        factura.id,
    )

    assert factura_completa is not None
    assert len(
        factura_completa.detalles,
    ) >= 1
    assert factura_completa.detalles[0].producto_id == producto.id


def test_flujo_venta_cotizacion_a_pedido_y_pdf_contenedor(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.integraciones.dian.contenedor_electronico import (
        adjuntos_contenedor_factura_venta,
    )
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )
    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )
    from aplicacion.modulos.ventas.cotizaciones.servicios import (
        ServicioCotizacion,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )
    from aplicacion.modulos.ventas.pedidos.servicios import (
        ServicioPedido,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}b"

    cliente = TerceroServicio.guardar(
        _datos_cliente(
            sufijo,
        ),
    )

    producto = ServicioProducto.guardar_completo(
        _datos_producto(
            sufijo,
            impuesto_id,
        ),
    )

    cotizacion = ServicioCotizacion.guardar_completa(
        {
            "cliente_id": cliente.id,
            "fecha": date.today(),
            "estado": "borrador",
            "activo": True,
        },
        [
            {
                "producto_id": producto.id,
                "descripcion": producto.nombre,
                "cantidad": 1,
                "precio_unitario": 25000,
                "impuesto_id": impuesto_id,
                "precio_incluye_iva": False,
            },
        ],
    )

    _confirmar_cotizacion_demo(
        cotizacion.id,
    )

    pedido = ServicioPedido.crear_desde_cotizacion(
        cotizacion.id,
    )

    assert pedido.cotizacion_id == cotizacion.id
    assert pedido.cliente_id == cliente.id
    assert pedido.estado == "borrador"

    pedido_confirmado = _confirmar_pedido_demo(
        pedido.id,
    )

    assert pedido_confirmado.estado == "pendiente"

    factura = ServicioFacturaVenta.crear_desde_cotizacion(
        cotizacion.id,
    )

    factura_completa = ServicioFacturaVenta.obtener_completa(
        factura.id,
    )

    adjuntos = adjuntos_contenedor_factura_venta(
        factura_completa,
        nombre_xml=f"fv-{sufijo}.xml",
        cufe=f"CUFE-DEMO-{sufijo}",
    )

    assert adjuntos is not None
    assert len(
        adjuntos,
    ) == 1
    assert adjuntos[0][1][:4] == b"%PDF"


def test_flujo_venta_cotizacion_a_remision(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.ventas.remisiones.servicios import (
        ServicioRemision,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}r"

    cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    _confirmar_cotizacion_demo(
        cotizacion.id,
    )

    remision = ServicioRemision.crear_desde_cotizacion(
        cotizacion.id,
    )

    assert remision.cotizacion_id == cotizacion.id
    assert remision.cliente_id == cliente.id
    assert remision.estado == "borrador"

    remision_confirmada = _confirmar_remision_demo(
        remision.id,
    )

    assert remision_confirmada.estado == "pendiente"


def test_flujo_venta_cotizacion_borrador_bloquea_documentos(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.ventas.pedidos.servicios import (
        ServicioPedido,
    )
    from aplicacion.modulos.ventas.remisiones.servicios import (
        ServicioRemision,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}cb"

    _cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    assert cotizacion.estado == "borrador"

    with pytest.raises(
        ValueError,
        match="Confirme la cotización",
    ):
        ServicioPedido.crear_desde_cotizacion(
            cotizacion.id,
        )

    with pytest.raises(
        ValueError,
        match="Confirme la cotización",
    ):
        ServicioRemision.crear_desde_cotizacion(
            cotizacion.id,
        )


def test_flujo_venta_pedido_confirmar_habilita_operaciones(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.ventas.pedidos.servicios import (
        ServicioPedido,
    )
    from aplicacion.modulos.ventas.remisiones.servicios import (
        ServicioRemision,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}pc"

    _cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    with pytest.raises(
        ValueError,
        match="Confirme la cotización",
    ):
        ServicioPedido.crear_desde_cotizacion(
            cotizacion.id,
        )

    _confirmar_cotizacion_demo(
        cotizacion.id,
    )

    pedido = ServicioPedido.crear_desde_cotizacion(
        cotizacion.id,
    )

    with pytest.raises(
        ValueError,
        match="Confirme el pedido",
    ):
        ServicioRemision.crear_desde_pedido(
            pedido.id,
        )

    pedido_confirmado = _confirmar_pedido_demo(
        pedido.id,
    )

    remision = ServicioRemision.crear_desde_pedido(
        pedido_confirmado.id,
    )

    assert remision.pedido_id == pedido.id
    assert remision.estado == "borrador"


def test_flujo_venta_confirmar_contabiliza_automatico(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.ventas.facturas.integracion import (
        IntegracionFacturaVenta,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}c"

    _cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    _confirmar_cotizacion_demo(
        cotizacion.id,
    )

    factura = ServicioFacturaVenta.crear_desde_cotizacion(
        cotizacion.id,
    )

    assert factura.estado == "borrador"

    factura_confirmada = IntegracionFacturaVenta.confirmar_venta(
        factura.id,
        emitir_dian=False,
    )

    assert factura_confirmada is not None
    assert factura_confirmada.estado == "contabilizada"
    assert factura_confirmada.contabilizado is True
    assert factura_confirmada.asiento_id is not None


def test_flujo_venta_remision_despacho_a_factura_sin_doble_inventario(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.ventas.facturas.integracion import (
        IntegracionFacturaVenta,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )
    from aplicacion.modulos.ventas.remisiones.servicios import (
        ServicioRemision,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}i"

    _cliente, producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    stock_inicial = _disponible_en_bodega(
        producto.id,
    )

    _confirmar_cotizacion_demo(
        cotizacion.id,
    )

    remision = ServicioRemision.crear_desde_cotizacion(
        cotizacion.id,
    )

    _confirmar_remision_demo(
        remision.id,
    )

    ServicioRemision.despachar(
        remision.id,
    )

    remision_despachada = ServicioRemision.obtener_completa(
        remision.id,
    )

    assert remision_despachada.inventario_aplicado is True
    assert remision_despachada.estado == "despachada"

    stock_tras_despacho = _disponible_en_bodega(
        producto.id,
    )

    assert stock_tras_despacho == stock_inicial - 1

    assert _contar_movimientos_inventario(
        "remision_venta",
        remision.id,
    ) == 1

    factura = ServicioFacturaVenta.crear_desde_remision(
        remision.id,
    )

    assert factura.cotizacion_id == cotizacion.id

    factura_confirmada = IntegracionFacturaVenta.confirmar_venta(
        factura.id,
        emitir_dian=False,
    )

    assert factura_confirmada.inventario_aplicado is True

    stock_final = _disponible_en_bodega(
        producto.id,
    )

    assert stock_final == stock_tras_despacho

    assert _contar_movimientos_inventario(
        "factura_venta",
        factura.id,
    ) == 0


def test_flujo_venta_nota_credito_desde_factura_confirmada(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.ventas.notas_credito.servicios import (
        ServicioNotaCreditoVenta,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}nc"

    _cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    factura = _confirmar_factura_demo(
        cotizacion.id,
    )

    nota = ServicioNotaCreditoVenta.crear_desde_factura(
        factura.id,
        motivo="Devolución parcial",
    )

    assert nota.factura_id == factura.id
    assert nota.cliente_id == factura.cliente_id
    assert nota.estado == "borrador"

    nota_completa = ServicioNotaCreditoVenta.obtener_completa(
        nota.id,
    )

    assert len(
        nota_completa.detalles,
    ) >= 1


def test_flujo_venta_nota_debito_desde_factura_confirmada(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.ventas.notas_debito.servicios import (
        ServicioNotaDebitoVenta,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}nd"

    _cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    factura = _confirmar_factura_demo(
        cotizacion.id,
    )

    nota = ServicioNotaDebitoVenta.crear_desde_factura(
        factura.id,
        motivo="Intereses mora",
    )

    assert nota.factura_id == factura.id
    assert nota.cliente_id == factura.cliente_id
    assert nota.estado == "borrador"


def test_flujo_venta_nota_credito_confirmar_revierte_inventario_y_saldo(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )
    from aplicacion.modulos.ventas.notas_credito.integracion import (
        IntegracionNotaCreditoVenta,
    )
    from aplicacion.modulos.ventas.notas_credito.servicios import (
        ServicioNotaCreditoVenta,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}ncf"

    _cliente, producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    stock_inicial = _disponible_en_bodega(
        producto.id,
    )

    factura = _confirmar_factura_demo(
        cotizacion.id,
    )

    stock_tras_factura = _disponible_en_bodega(
        producto.id,
    )

    assert stock_tras_factura == stock_inicial - 1

    saldo_inicial = float(
        factura.saldo_pendiente or 0,
    )

    assert saldo_inicial > 0

    nota = ServicioNotaCreditoVenta.crear_desde_factura(
        factura.id,
        motivo="Devolución total",
    )

    nota_confirmada = IntegracionNotaCreditoVenta.confirmar_generacion(
        nota.id,
        emitir_dian=False,
    )

    assert nota_confirmada.contabilizado is True
    assert nota_confirmada.inventario_aplicado is True

    assert _contar_movimientos_inventario(
        "nota_credito_venta",
        nota.id,
    ) == 1

    stock_tras_nc = _disponible_en_bodega(
        producto.id,
    )

    assert stock_tras_nc == stock_inicial

    factura_actualizada = ServicioFacturaVenta.obtener_completa(
        factura.id,
    )

    assert float(
        factura_actualizada.saldo_pendiente or 0,
    ) < saldo_inicial


def test_flujo_venta_nota_debito_confirmar_aumenta_saldo(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )
    from aplicacion.modulos.ventas.notas_debito.integracion import (
        IntegracionNotaDebitoVenta,
    )
    from aplicacion.modulos.ventas.notas_debito.servicios import (
        ServicioNotaDebitoVenta,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}ndf"

    _cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    factura = _confirmar_factura_demo(
        cotizacion.id,
    )

    saldo_inicial = float(
        factura.saldo_pendiente or 0,
    )

    nota = ServicioNotaDebitoVenta.crear_desde_factura(
        factura.id,
        motivo="Intereses mora",
    )

    nota = ServicioNotaDebitoVenta.guardar_completa(
        {
            "numero": nota.numero,
            "cliente_id": nota.cliente_id,
            "factura_id": nota.factura_id,
            "motivo": nota.motivo,
            "fecha": nota.fecha,
            "estado": nota.estado,
            "activo": True,
        },
        [
            {
                "descripcion": "Intereses mora",
                "cantidad": 1,
                "precio_unitario": 5000,
                "impuesto_id": impuesto_id,
                "precio_incluye_iva": False,
            },
        ],
        id_registro=nota.id,
    )

    nota_confirmada = IntegracionNotaDebitoVenta.confirmar_generacion(
        nota.id,
        emitir_dian=False,
    )

    assert nota_confirmada.contabilizado is True

    factura_actualizada = ServicioFacturaVenta.obtener_completa(
        factura.id,
    )

    assert float(
        factura_actualizada.saldo_pendiente or 0,
    ) > saldo_inicial


def test_flujo_tesoreria_recibo_caja_aplica_abono_parcial(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.cartera.servicios import (
        ServicioCartera,
    )
    from aplicacion.modulos.tesoreria.recibos_caja.integracion import (
        IntegracionReciboCaja,
    )
    from aplicacion.modulos.tesoreria.recibos_caja.servicios import (
        ServicioReciboCaja,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}rc"

    cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    factura = _confirmar_factura_demo(
        cotizacion.id,
    )

    saldo_inicial = float(
        factura.saldo_pendiente or 0,
    )

    abono = round(
        saldo_inicial / 2,
        2,
    )

    recibo = ServicioReciboCaja.guardar_completo(
        {
            "cliente_id": cliente.id,
            "forma_pago": "efectivo",
            "es_anticipo": False,
        },
        [
            {
                "factura_venta_id": factura.id,
                "valor_aplicado": abono,
            },
        ],
    )

    IntegracionReciboCaja.contabilizar(
        recibo.id,
    )

    factura_actualizada = ServicioFacturaVenta.obtener_completa(
        factura.id,
    )

    assert float(
        factura_actualizada.saldo_pendiente or 0,
    ) == pytest.approx(
        saldo_inicial - abono,
        rel=0,
        abs=0.02,
    )

    recibo_actualizado = ServicioReciboCaja.obtener_completo(
        recibo.id,
    )

    assert recibo_actualizado.contabilizado is True
    assert recibo_actualizado.estado == "contabilizado"

    resumen = ServicioCartera.resumen()

    assert resumen["cxc_total"] >= float(
        factura_actualizada.saldo_pendiente or 0,
    )


def test_flujo_cartera_resumen_cliente_desde_factura(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.cartera.servicios import (
        ServicioCartera,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}cxc"

    cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    factura = _confirmar_factura_demo(
        cotizacion.id,
    )

    resumen = ServicioCartera.resumen_cliente_cxc(
        cliente.id,
    )

    assert resumen["facturas_pendientes"] >= 1
    assert resumen["saldo_total"] >= float(
        factura.saldo_pendiente or 0,
    )


def test_reporte_pipeline_comercial_muestra_cadena_factura(
    requiere_postgresql,
    sufijo_unico,
):
    from aplicacion.modulos.reportes.servicios import (
        ServicioReportes,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}pip"

    _cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    factura = _confirmar_factura_demo(
        cotizacion.id,
    )

    filas = ServicioReportes.pipeline_comercial(
        fecha_desde=cotizacion.fecha,
        fecha_hasta=cotizacion.fecha,
    )

    fila = next(
        (
            item
            for item in filas
            if item["cotizacion_numero"]
            == cotizacion.numero
        ),
        None,
    )

    assert fila is not None
    assert fila["factura_numero"] == factura.numero
    assert fila["etapa_actual"] == "factura"
    assert fila["cotizacion_estado"] == "aprobada"
    assert float(
        fila["saldo_pendiente"],
    ) > 0


@pytest.mark.e2e
def test_flujo_e2e_comercial_completo(
    requiere_postgresql,
    sufijo_unico,
):
    """Cadena integrada: cotización → factura → NC → recibo parcial."""

    from aplicacion.modulos.tesoreria.recibos_caja.integracion import (
        IntegracionReciboCaja,
    )
    from aplicacion.modulos.tesoreria.recibos_caja.servicios import (
        ServicioReciboCaja,
    )
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )
    from aplicacion.modulos.ventas.notas_credito.integracion import (
        IntegracionNotaCreditoVenta,
    )

    impuesto_id = _preparar_maestros()

    sufijo = f"{sufijo_unico}e2e"

    cliente, _producto, cotizacion = _crear_cotizacion_demo(
        sufijo=sufijo,
        impuesto_id=impuesto_id,
    )

    factura = _confirmar_factura_demo(
        cotizacion.id,
    )

    saldo_tras_factura = float(
        factura.saldo_pendiente or 0,
    )

    nota = _nota_credito_parcial_desde_factura(
        factura.id,
        motivo="Devolución E2E",
        factor=0.5,
    )

    IntegracionNotaCreditoVenta.confirmar_generacion(
        nota.id,
        emitir_dian=False,
    )

    factura_tras_nc = ServicioFacturaVenta.obtener_completa(
        factura.id,
    )

    saldo_tras_nc = float(
        factura_tras_nc.saldo_pendiente or 0,
    )

    assert saldo_tras_nc < saldo_tras_factura
    assert saldo_tras_nc > 0

    abono = round(
        saldo_tras_nc / 2,
        2,
    )

    assert abono > 0

    recibo = ServicioReciboCaja.guardar_completo(
        {
            "cliente_id": cliente.id,
            "forma_pago": "efectivo",
            "es_anticipo": False,
        },
        [
            {
                "factura_venta_id": factura.id,
                "valor_aplicado": abono,
            },
        ],
    )

    IntegracionReciboCaja.contabilizar(
        recibo.id,
    )

    factura_final = ServicioFacturaVenta.obtener_completa(
        factura.id,
    )

    assert float(
        factura_final.saldo_pendiente or 0,
    ) == pytest.approx(
        saldo_tras_nc - abono,
        rel=0,
        abs=0.02,
    )
