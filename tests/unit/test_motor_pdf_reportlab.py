from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

from aplicacion.framework.reportes.motor_documento import (
    exportar_pdf_reporte,
    resolver_motor_pdf,
)
from aplicacion.reportes.comunes.datos_documento import (
    factura_venta_a_dto,
)
from aplicacion.reportes.ventas.cotizacion import (
    crear_reporte_cotizacion,
)
from aplicacion.reportes.ventas.factura import (
    ReporteFacturaVenta,
)
from aplicacion.reportes.ventas.factura_electronica import (
    ReporteFacturaElectronicaVenta,
)
from aplicacion.reportes.ventas.pedido import (
    crear_reporte_pedido,
)
from aplicacion.reportes.ventas.remision import (
    crear_reporte_remision,
)
from aplicacion.reportes.compras.factura import (
    crear_reporte_factura_compra,
)
from aplicacion.reportes.compras.orden_compra import (
    crear_reporte_orden_compra,
)
from aplicacion.reportes.tesoreria.comprobante_egreso import (
    crear_reporte_comprobante_egreso,
)
from aplicacion.reportes.tesoreria.recibo_caja import (
    crear_reporte_recibo_caja,
)
from aplicacion.reportes.inventario.ajuste import (
    crear_reporte_ajuste_inventario,
)
from aplicacion.reportes.inventario.entrada import (
    crear_reporte_entrada_inventario,
)
from aplicacion.reportes.inventario.kardex import (
    crear_reporte_kardex,
)
from aplicacion.reportes.inventario.salida import (
    crear_reporte_salida_inventario,
)
from aplicacion.reportes.inventario.traslado import (
    crear_reporte_traslado_inventario,
)
from aplicacion.reportes.ventas.nota_credito import (
    crear_reporte_nota_credito_venta,
)
from aplicacion.reportes.ventas.nota_debito import (
    crear_reporte_nota_debito_venta,
)
from aplicacion.reportes.contabilidad.comprobante_contable import (
    crear_reporte_comprobante_contable,
)
from aplicacion.reportes.contabilidad.balance_prueba import (
    crear_reporte_balance_prueba,
)
from aplicacion.reportes.contabilidad.libro_mayor import (
    crear_reporte_libro_mayor,
)
from aplicacion.reportes.contabilidad.estado_resultados import (
    crear_reporte_estado_resultados,
)
from aplicacion.reportes.cartera.estado_cuenta import (
    crear_reporte_estado_cuenta_cxc,
)
from aplicacion.reportes.cartera.reportes import (
    crear_reporte_antiguedad_cartera,
    crear_reporte_resumen_cartera,
)
from aplicacion.framework.reportes.reporte_tabla import (
    crear_reporte_tabla,
)
from aplicacion.reportes.reportes_periodo import (
    crear_reporte_periodo,
)


def _detalle_ejemplo() -> MagicMock:

    detalle = MagicMock()
    detalle.descripcion = "Producto A"
    detalle.cantidad = 2
    detalle.precio_unitario = 50000
    detalle.total_linea = 100000
    detalle.impuesto_id = None
    detalle.producto_id = None
    detalle.precio_incluye_iva = False
    detalle.descuento = 0

    return detalle


def _factura_ejemplo() -> MagicMock:

    factura = MagicMock()
    factura.numero = "FV-00001234"
    factura.fecha = date(
        2026,
        8,
        10,
    )
    factura.fecha_vencimiento = date(
        2026,
        9,
        10,
    )
    factura.fecha_creacion = None
    factura.subtotal = 180000
    factura.iva = 32300
    factura.total = 202300
    factura.estado_pago = "credito"
    factura.cufe = (
        "a1b2c3d4e5f6789012345678901234567890abcd"
    )
    factura.estado_dian = "Aceptada"
    factura.observaciones = "Entrega en bodega."
    factura.cliente_id = 1
    factura.consecutivo_dian = "990000001"

    return factura


@patch(
    "aplicacion.reportes.comunes.datos_documento._datos_empresa",
    return_value={
        "nombre": "Empresa Demo S.A.S.",
        "nit": "900.123.456-7",
        "direccion": "Calle 123",
        "ciudad": "Bogotá",
        "telefono": "6011234567",
    },
)
@patch(
    "aplicacion.reportes.comunes.datos_documento._datos_cliente",
    return_value={
        "nombre": "Cliente XYZ S.A.S.",
        "nit": "800.123.456-1",
        "direccion": "Carrera 10",
        "ciudad": "Bogotá",
        "telefono": "3001234567",
        "correo": "cliente@demo.com",
    },
)
@patch(
    "aplicacion.reportes.comunes.datos_documento._unidad_producto",
    return_value="UND",
)
@patch(
    "aplicacion.reportes.comunes.datos_documento._porcentaje_impuesto_id",
    return_value=0.0,
)
@patch(
    "aplicacion.nucleo.configuracion.Configuracion.obtener",
    side_effect=lambda seccion, clave, default=None: {
        (
            "dian",
            "resolucion_numero",
        ): "18760000001",
        (
            "dian",
            "url_catalogo_cufe",
        ): (
            "https://catalogo-vpfe.dian.gov.co/document/searchqr"
        ),
    }.get(
        (
            seccion,
            clave,
        ),
        default,
    ),
)
def test_factura_venta_a_dto_incluye_campos_electronicos(
    *_mocks,
):

    dto = factura_venta_a_dto(
        _factura_ejemplo(),
        [
            _detalle_ejemplo(),
        ],
        "Cliente XYZ S.A.S.",
        electronica=True,
    )

    assert dto["numero"] == "FV-00001234"
    assert dto["cufe"]
    assert "documentkey=" in dto["qr_url"]
    assert dto["cliente"]["documento"] == "800.123.456-1"
    assert len(
        dto["items"],
    ) == 1


def _nota_venta_ejemplo() -> MagicMock:

    nota = MagicMock()
    nota.numero = "NC-00001234"
    nota.fecha = date(
        2026,
        8,
        10,
    )
    nota.fecha_creacion = None
    nota.subtotal = 180000
    nota.iva = 32300
    nota.total = 202300
    nota.cufe = (
        "a1b2c3d4e5f6789012345678901234567890abcd"
    )
    nota.estado_dian = "Aceptada"
    nota.observaciones = ""
    nota.cliente_id = 1
    nota.consecutivo_dian = "990000002"
    nota.factura_id = 10
    nota.factura_cufe = "cufe-factura-ref"
    nota.motivo = "Devolución parcial"

    return nota


def test_pdf_nota_credito_venta(
    tmp_path: Path,
):

    reporte = crear_reporte_nota_credito_venta(
        _nota_venta_ejemplo(),
        [
            _detalle_ejemplo(),
        ],
        "Cliente XYZ S.A.S.",
        factura_numero="FV-00001",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_nota_debito_venta(
    tmp_path: Path,
):

    nota = _nota_venta_ejemplo()
    nota.numero = "ND-00001234"

    reporte = crear_reporte_nota_debito_venta(
        nota,
        [
            _detalle_ejemplo(),
        ],
        "Cliente XYZ S.A.S.",
        factura_numero="FV-00001",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_comprobante_contable(
    tmp_path: Path,
):

    cuenta = MagicMock()
    cuenta.codigo = "110505"
    cuenta.nombre = "Caja general"

    detalle = MagicMock()
    detalle.cuenta = cuenta
    detalle.debito = 100000
    detalle.credito = 0
    detalle.descripcion = "Registro manual"

    asiento = MagicMock()
    asiento.numero = "CC-00001"
    asiento.fecha = date(
        2026,
        8,
        10,
    )
    asiento.origen = "manual"
    asiento.descripcion = "Asiento de prueba"
    asiento.total_debito = 100000
    asiento.total_credito = 100000
    asiento.detalles = [
        detalle,
    ]

    reporte = crear_reporte_comprobante_contable(
        asiento,
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_balance_prueba(
    tmp_path: Path,
):

    resultado = {
        "filas": [
            {
                "codigo": "110505",
                "nombre": "Caja",
                "debito": 100000,
                "credito": 50000,
                "saldo": 50000,
            },
        ],
        "total_debito": 100000,
        "total_credito": 50000,
    }

    reporte = crear_reporte_balance_prueba(
        resultado,
        periodo="01/08/2026 - 10/08/2026",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_estado_cuenta_cxc(
    tmp_path: Path,
):

    resultado = {
        "tercero": "Cliente Demo S.A.S.",
        "saldo_final": 150000,
        "movimientos": [
            {
                "fecha": date(
                    2026,
                    8,
                    10,
                ),
                "documento": "FV-001",
                "tipo": "Factura",
                "debito": 200000,
                "credito": 0,
                "saldo": 200000,
                "referencia": "Vence 10/09/2026",
            },
            {
                "fecha": date(
                    2026,
                    8,
                    15,
                ),
                "documento": "RC-001",
                "tipo": "Recibo",
                "debito": 0,
                "credito": 50000,
                "saldo": 150000,
                "referencia": "Factura FV-001",
            },
        ],
    }

    reporte = crear_reporte_estado_cuenta_cxc(
        resultado,
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def _assert_pdf_reportlab(
    reporte,
    tmp_path: Path,
):

    with patch(
        "aplicacion.reportes.comunes.datos_documento._datos_empresa",
        return_value={
            "nombre": "Empresa Demo S.A.S.",
            "nit": "900.123.456-7",
            "direccion": "Calle 123",
            "ciudad": "Bogotá",
            "telefono": "6011234567",
        },
    ), patch(
        "aplicacion.reportes.comunes.datos_documento._datos_cliente",
        return_value={
            "nombre": "Cliente XYZ S.A.S.",
            "nit": "800.123.456-1",
            "direccion": "Carrera 10",
            "ciudad": "Bogotá",
            "telefono": "3001234567",
            "correo": "cliente@demo.com",
        },
    ), patch(
        "aplicacion.reportes.comunes.datos_documento._unidad_producto",
        return_value="UND",
    ), patch(
        "aplicacion.reportes.comunes.datos_documento._porcentaje_impuesto_id",
        return_value=0.0,
    ), patch(
        "aplicacion.reportes.comunes.datos_documento._proveedor_desde_documento",
        return_value={
            "nombre": "Proveedor Demo S.A.S.",
            "documento": "800.111.222-3",
            "direccion": "Calle 50",
            "ciudad": "Medellín",
            "telefono": "6041234567",
            "correo": "proveedor@demo.com",
        },
    ), patch(
        "aplicacion.reportes.comunes.datos_documento._lineas_recibo_caja",
        return_value=[
            {
                "numero": 1,
                "documento": "Factura FV-001",
                "valor": 150000,
                "valor_aplicado": 150000,
                "saldo_anterior": 350000,
                "saldo_restante": 200000,
            },
        ],
    ), patch(
        "aplicacion.reportes.comunes.datos_documento._lineas_comprobante_egreso",
        return_value=[
            {
                "numero": 1,
                "documento": "FC FC-001",
                "valor": 250000,
                "valor_aplicado": 250000,
                "saldo_anterior": 500000,
                "saldo_restante": 250000,
            },
        ],
    ), patch(
        "aplicacion.reportes.comunes.datos_inventario._etiqueta_bodega",
        return_value="BOD-01 - Principal",
    ), patch(
        "aplicacion.reportes.comunes.datos_inventario._linea_producto_movimiento",
        side_effect=lambda movimiento, indice: {
            "numero": indice,
            "codigo": "PROD-01",
            "descripcion": "Producto demo",
            "cantidad": float(
                getattr(
                    movimiento,
                    "cantidad",
                    1,
                )
                or 1,
            ),
            "unidad": "UND",
            "costo": float(
                getattr(
                    movimiento,
                    "costo_unitario",
                    0,
                )
                or 0,
            ),
            "total": float(
                getattr(
                    movimiento,
                    "cantidad",
                    1,
                )
                or 1,
            )
            * float(
                getattr(
                    movimiento,
                    "costo_unitario",
                    0,
                )
                or 0,
            ),
        },
    ), patch(
        "aplicacion.reportes.comunes.datos_inventario._resolver_referencia_texto",
        return_value="Ajuste manual",
    ):

        assert reporte.soporta_pdf_reportlab()

        destino = tmp_path / "documento.pdf"

        ruta = reporte.construir_pdf_reportlab(
            destino,
        )

        assert ruta.exists()
        assert ruta.stat().st_size > 500
        assert ruta.read_bytes()[
            :4
        ] == b"%PDF"


def test_pdf_factura_venta(
    tmp_path: Path,
):

    reporte = ReporteFacturaVenta(
        _factura_ejemplo(),
        [
            _detalle_ejemplo(),
        ],
        "Cliente XYZ S.A.S.",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_factura_electronica(
    tmp_path: Path,
):

    ctx = MagicMock(
        cotizacion=_factura_ejemplo(),
        detalles=[
            _detalle_ejemplo(),
        ],
        nombre_cliente="Cliente XYZ S.A.S.",
    )

    reporte = ReporteFacturaElectronicaVenta(
        ctx,
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_cotizacion(
    tmp_path: Path,
):

    reporte = crear_reporte_cotizacion(
        _factura_ejemplo(),
        [
            _detalle_ejemplo(),
        ],
        "Cliente XYZ S.A.S.",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_pedido(
    tmp_path: Path,
):

    reporte = crear_reporte_pedido(
        _factura_ejemplo(),
        [
            _detalle_ejemplo(),
        ],
        "Cliente XYZ S.A.S.",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_remision(
    tmp_path: Path,
):

    reporte = crear_reporte_remision(
        _factura_ejemplo(),
        [
            _detalle_ejemplo(),
        ],
        "Cliente XYZ S.A.S.",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def _detalle_compra_ejemplo() -> MagicMock:

    detalle = MagicMock()
    detalle.descripcion = "Insumo A"
    detalle.cantidad = 5
    detalle.precio_unitario = 20000
    detalle.costo_unitario = 20000
    detalle.total_linea = 100000
    detalle.cantidad_recibida = 0
    detalle.impuesto_id = None
    detalle.precio_incluye_iva = False

    return detalle


def _factura_compra_ejemplo() -> MagicMock:

    factura = MagicMock()
    factura.numero = "FC-00001"
    factura.fecha = date(
        2026,
        8,
        10,
    )
    factura.subtotal = 100000
    factura.iva = 19000
    factura.total = 119000
    factura.estado = "registrada"
    factura.origen = "manual"
    factura.observaciones = "Compra mensual"
    factura.cufe = ""
    factura.numero_proveedor = "FP-7788"
    factura.proveedor_id = None

    return factura


def test_pdf_factura_compra(
    tmp_path: Path,
):

    reporte = crear_reporte_factura_compra(
        _factura_compra_ejemplo(),
        [
            _detalle_compra_ejemplo(),
        ],
        "Proveedor Demo S.A.S.",
        proveedor=None,
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_orden_compra(
    tmp_path: Path,
):

    orden = MagicMock()
    orden.numero = "OC-00001"
    orden.fecha = date(
        2026,
        8,
        10,
    )
    orden.subtotal = 100000
    orden.total = 100000
    orden.estado = "pendiente"
    orden.observaciones = ""
    orden.proveedor_id = None

    reporte = crear_reporte_orden_compra(
        orden,
        [
            _detalle_compra_ejemplo(),
        ],
        "Proveedor Demo S.A.S.",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_recibo_caja(
    tmp_path: Path,
):

    recibo = MagicMock()
    recibo.numero = "RC-00001"
    recibo.fecha = date(
        2026,
        8,
        10,
    )
    recibo.valor_total = 150000
    recibo.forma_pago = "transferencia"
    recibo.estado = "aplicado"
    recibo.observaciones = "Abono factura"
    recibo.detalles = []

    reporte = crear_reporte_recibo_caja(
        recibo,
        nombre_cliente="Cliente Demo",
        documento_cliente="900.111.222-3",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_comprobante_egreso(
    tmp_path: Path,
):

    comprobante = MagicMock()
    comprobante.numero = "CE-00001"
    comprobante.fecha = date(
        2026,
        8,
        10,
    )
    comprobante.valor_total = 250000
    comprobante.forma_pago = "transferencia"
    comprobante.estado = "aplicado"
    comprobante.observaciones = "Pago proveedor"
    comprobante.detalles = []

    reporte = crear_reporte_comprobante_egreso(
        comprobante,
        nombre_proveedor="Proveedor Demo",
        documento_proveedor="800.111.222-3",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def _movimiento_ejemplo(
    *,
    tipo: str = "entrada",
) -> MagicMock:

    movimiento = MagicMock()
    movimiento.id = 42
    movimiento.bodega_id = 1
    movimiento.producto_id = 10
    movimiento.producto_variante_id = None
    movimiento.tipo = tipo
    movimiento.cantidad = 5
    movimiento.costo_unitario = 20000
    movimiento.referencia = "ajuste"
    movimiento.referencia_id = None
    movimiento.fecha = date(
        2026,
        8,
        10,
    )
    movimiento.observaciones = "Movimiento de prueba"

    return movimiento


def test_pdf_entrada_inventario(
    tmp_path: Path,
):

    reporte = crear_reporte_entrada_inventario(
        _movimiento_ejemplo(
            tipo="entrada",
        ),
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_salida_inventario(
    tmp_path: Path,
):

    reporte = crear_reporte_salida_inventario(
        _movimiento_ejemplo(
            tipo="salida",
        ),
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_ajuste_inventario(
    tmp_path: Path,
):

    reporte = crear_reporte_ajuste_inventario(
        _movimiento_ejemplo(
            tipo="entrada",
        ),
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_traslado_inventario(
    tmp_path: Path,
):

    salida = _movimiento_ejemplo(
        tipo="salida",
    )
    salida.id = 50
    salida.referencia = "traslado"
    salida.referencia_id = 2

    entrada = _movimiento_ejemplo(
        tipo="entrada",
    )
    entrada.id = 51
    entrada.bodega_id = 2

    reporte = crear_reporte_traslado_inventario(
        salida,
        entrada,
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_kardex_inventario(
    tmp_path: Path,
):

    filas = [
        {
            "fecha": date(
                2026,
                8,
                10,
            ),
            "bodega": "BOD-01 - Principal",
            "codigo": "PROD-01",
            "producto": "Producto demo",
            "variante": "",
            "tipo": "entrada",
            "cantidad": 5,
            "costo_unitario": 20000,
            "referencia": "ajuste",
            "saldo": 5,
        },
    ]

    reporte = crear_reporte_kardex(
        filas,
        numero="01/08/2026 - 10/08/2026",
        subtitulo="Bodega: Todas | Producto: Todos",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_libro_mayor(
    tmp_path: Path,
):

    cuenta = MagicMock()
    cuenta.codigo = "110505"
    cuenta.nombre = "Caja general"

    resultado = {
        "cuenta": cuenta,
        "filas": [
            {
                "fecha": date(
                    2026,
                    8,
                    10,
                ),
                "numero": "CC-001",
                "descripcion": "Registro",
                "debito": 100000,
                "credito": 0,
                "saldo": 100000,
            },
        ],
    }

    reporte = crear_reporte_libro_mayor(
        resultado,
        periodo="01/08/2026 - 10/08/2026",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_estado_resultados(
    tmp_path: Path,
):

    resultado = {
        "ingresos": [
            {
                "codigo": "413501",
                "nombre": "Ingresos por ventas",
                "tipo": "ingreso",
                "valor": 500000,
            },
        ],
        "costos_venta": [
            {
                "codigo": "613505",
                "nombre": "Costo de ventas",
                "tipo": "gasto",
                "valor": 200000,
            },
        ],
        "gastos": [
            {
                "codigo": "613501",
                "nombre": "Compras de mercancía",
                "tipo": "gasto",
                "valor": 50000,
            },
        ],
        "total_ingresos": 500000,
        "total_costos_venta": 200000,
        "total_gastos": 50000,
        "utilidad_bruta": 300000,
        "utilidad_neta": 250000,
    }

    reporte = crear_reporte_estado_resultados(
        resultado,
        periodo="01/08/2026 - 10/08/2026",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_reporte_tabla_generico(
    tmp_path: Path,
):

    reporte = crear_reporte_tabla(
        titulo="Existencias de inventario",
        numero="Todas",
        subtitulo="Solo con stock",
        columnas=[
            "Código",
            "Producto",
            "Existencia",
        ],
        filas=[
            [
                "PROD-01",
                "Producto demo",
                "10,00",
            ],
        ],
        nombre_pdf="Existencias.pdf",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_reporte_periodo_ventas(
    tmp_path: Path,
):

    filas = [
        {
            "numero": "FV-001",
            "fecha": date(
                2026,
                8,
                10,
            ),
            "cliente": "Cliente Demo",
            "total": 119000,
        },
    ]

    reporte = crear_reporte_periodo(
        titulo="Ventas por periodo",
        filas=filas,
        columnas=[
            "Número",
            "Fecha",
            "Cliente",
            "Total",
        ],
        campos=[
            "numero",
            "fecha",
            "cliente",
            "total",
        ],
        periodo="01/08/2026 - 10/08/2026",
        columnas_numericas={3},
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_antiguedad_cartera(
    tmp_path: Path,
):

    filas = [
        {
            "rango": "Al día",
            "saldo": 50000,
        },
    ]

    reporte = crear_reporte_antiguedad_cartera(
        filas,
        titulo_cartera="Cuentas por cobrar",
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


def test_pdf_resumen_cartera(
    tmp_path: Path,
):

    filas = [
        {
            "concepto": "Por cobrar",
            "valor": 150000,
        },
    ]

    reporte = crear_reporte_resumen_cartera(
        filas,
    )

    _assert_pdf_reportlab(
        reporte,
        tmp_path,
    )


@patch(
    "aplicacion.nucleo.configuracion.Configuracion.obtener",
    side_effect=lambda seccion, clave, default=None: {
        (
            "impresion",
            "motor_pdf",
        ): "auto",
    }.get(
        (
            seccion,
            clave,
        ),
        default,
    ),
)
def test_resolver_motor_pdf_auto_usa_reportlab(
    _mock_config,
):

    reporte = MagicMock()
    reporte.soporta_pdf_reportlab.return_value = True

    assert (
        resolver_motor_pdf(
            reporte,
        )
        == "reportlab"
    )


@patch(
    "aplicacion.framework.reportes.motor_documento.exportar_html_pdf",
    return_value="/tmp/fallback.pdf",
)
@patch(
    "aplicacion.nucleo.configuracion.Configuracion.obtener",
    side_effect=lambda seccion, clave, default=None: {
        (
            "impresion",
            "motor_pdf",
        ): "reportlab",
        (
            "impresion",
            "motor_pdf_html_respaldo",
        ): True,
    }.get(
        (
            seccion,
            clave,
        ),
        default,
    ),
)
def test_exportar_pdf_reporte_fallback_html(
    mock_config,
    mock_html,
):

    reporte = MagicMock()
    reporte.formato_pagina_predeterminado.return_value = "carta"
    reporte.generar_html.return_value = "<html></html>"
    reporte.construir_pdf_reportlab.side_effect = RuntimeError(
        "fallo reportlab",
    )

    resultado = exportar_pdf_reporte(
        reporte,
        "/tmp/prueba.pdf",
    )

    assert resultado == "/tmp/fallback.pdf"
    mock_html.assert_called_once()
