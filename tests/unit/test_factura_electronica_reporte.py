from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    ContextoFormato,
)
from aplicacion.reportes.ventas.factura_electronica import (
    ReporteFacturaElectronicaVenta,
    generar_html_factura_electronica,
)


def _contexto_ejemplo() -> ContextoFormato:

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
    factura.estado = "emitida"
    factura.estado_pago = "pendiente"
    factura.estado_dian = "Aceptada"
    factura.cufe = (
        "a1b2c3d4e5f6789012345678901234567890abcd"
    )
    factura.observaciones = "Entrega en bodega principal."

    detalle = MagicMock()
    detalle.descripcion = "Producto A"
    detalle.cantidad = 2
    detalle.precio_unitario = 50000
    detalle.total_linea = 100000
    detalle.impuesto_id = 1
    detalle.producto_id = 10

    return ContextoFormato(
        cotizacion=factura,
        detalles=[
            detalle,
        ],
        nombre_cliente="Cliente XYZ S.A.S.",
        resumen={
            "subtotal": 180000,
            "iva": 32300,
            "total": 202300,
            "retefuente": 0,
            "reteica": 0,
        },
        empresa={
            "nombre": "Empresa Demo S.A.S.",
            "nit": "900.123.456-7",
            "direccion": "Calle 123 #45-67",
            "ciudad": "Bogotá",
            "telefono": "6011234567",
            "correo": "facturacion@demo.com",
            "notas_pie": "Gracias por su compra.",
        },
        cliente={
            "documento": "800.123.456-1",
            "direccion": "Carrera 10 #20-30",
            "telefono": "3001234567",
            "correo": "cliente@demo.com",
        },
        fecha="10/08/2026",
        observaciones="Entrega en bodega principal.",
        etiqueta_documento="FACTURA",
        titulo_documento="Factura",
        info_adicional="",
        mostrar_imagenes=False,
    )


@patch(
    "aplicacion.reportes.ventas.factura_electronica.generar_qr_data_uri",
    return_value="data:image/png;base64,QR",
)
@patch(
    "aplicacion.reportes.ventas.factura_electronica._etiqueta_impuesto_porcentaje",
    return_value="19%",
)
@patch(
    "aplicacion.reportes.ventas.factura_electronica._unidad_producto",
    return_value="UND",
)
def test_generar_html_factura_electronica_contiene_secciones(
    *_mocks,
):

    html = generar_html_factura_electronica(
        _contexto_ejemplo(),
    )

    assert "FACTURA ELECTRÓNICA DE VENTA" in html
    assert "FV-00001234" in html
    assert "Cliente XYZ S.A.S." in html
    assert "CUFE:" in html
    assert "data:image/png;base64,QR" in html
    assert "SON:" in html
    assert "Producto A" in html


def test_reporte_factura_electronica_nombre_pdf():

    reporte = ReporteFacturaElectronicaVenta(
        _contexto_ejemplo(),
    )

    assert reporte.numero_documento == "FV-00001234"
    assert reporte.nombre_archivo_pdf().endswith(
        ".pdf",
    )
    assert "Cliente XYZ" in reporte.nombre_archivo_pdf()


@patch(
    "aplicacion.modulos.ventas.facturas.formatos_impresion._datos_empresa",
    return_value={
        "nombre": "Empresa Demo",
        "nit": "900.123.456-7",
    },
)
@patch(
    "aplicacion.modulos.ventas.facturas.formatos_impresion._datos_cliente",
    return_value={
        "documento": "800.123.456-1",
    },
)
@patch(
    "aplicacion.reportes.ventas.factura_electronica.generar_html_factura_electronica",
    return_value="<html>FE</html>",
)
def test_generar_html_factura_venta_usa_plantilla_electronica(
    mock_fe,
    *_mocks,
):

    from aplicacion.modulos.ventas.facturas.formatos_impresion import (
        generar_html_factura_venta,
    )

    factura = MagicMock()
    factura.formato_impresion = "electronica"
    factura.fecha = date(
        2026,
        8,
        10,
    )
    factura.observaciones = ""

    html = generar_html_factura_venta(
        factura,
        [],
        "Cliente Demo",
        formato="electronica",
    )

    assert html == "<html>FE</html>"
    mock_fe.assert_called_once()
