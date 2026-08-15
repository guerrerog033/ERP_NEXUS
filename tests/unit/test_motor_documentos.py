from __future__ import annotations

from aplicacion.documentos.impresion.catalogo import (
    CATALOGO_DOCUMENTOS,
    obtener_entrada_catalogo,
)
from aplicacion.documentos.impresion.documento_datos import (
    dict_a_documento_datos,
    documento_datos_a_dict,
)
from aplicacion.documentos.impresion.formatos import (
    crear_renderer,
)


def test_catalogo_documentos_tiene_26_entradas():

    assert len(
        CATALOGO_DOCUMENTOS,
    ) == 26


def test_obtener_entrada_catalogo_factura():

    entrada = obtener_entrada_catalogo(
        "04_FACTURA_VENTA",
    )

    assert entrada is not None
    assert entrada.nombre == "Factura de venta"
    assert entrada.soporta_reportlab is True


def test_dict_a_documento_datos_mapea_totales():

    payload = {
        "numero": "FV-00001",
        "subtotal": 100000,
        "descuento": 5000,
        "impuestos": 18050,
        "total": 113050,
        "total_letras": "CIENTO TRECE MIL",
        "cliente": {
            "nombre": "Cliente Demo",
            "documento": "900123456",
        },
        "items": [
            {
                "descripcion": "Producto",
                "cantidad": 2,
                "precio": 50000,
                "total": 100000,
            },
        ],
    }

    datos = dict_a_documento_datos(
        payload,
        tipo="factura",
        codigo_catalogo="04_FACTURA_VENTA",
    )

    assert datos.numero == "FV-00001"
    assert float(
        datos.totales.total,
    ) == 113050.0
    assert datos.tercero.nombre == "Cliente Demo"
    assert len(
        datos.items,
    ) == 1

    roundtrip = documento_datos_a_dict(
        datos,
    )

    assert roundtrip["numero"] == "FV-00001"
    assert roundtrip["total"] == 113050.0


def test_crear_renderer_factura(tmp_path):

    payload = {
        "numero": "FV-00099",
        "fecha_generacion": "14/08/2026",
        "fecha_vencimiento": "14/09/2026",
        "forma_pago": "Crédito",
        "medio_pago": "Transferencia",
        "subtotal": 100000,
        "descuento": 0,
        "impuestos": 19000,
        "total": 119000,
        "total_letras": "CIENTO DIECINUEVE MIL",
        "empresa": {
            "razon_social": "Empresa Demo S.A.S.",
            "nit": "900123456",
            "direccion": "Calle 1",
            "ciudad": "Bogotá",
            "telefono": "6011234567",
        },
        "cliente": {
            "nombre": "Cliente Demo",
            "documento": "800987654",
            "direccion": "Carrera 7",
            "ciudad": "Bogotá",
        },
        "items": [
            {
                "numero": 1,
                "descripcion": "Servicio",
                "cantidad": 1,
                "precio": 100000,
                "descuento": 0,
                "impuestos": 19000,
                "total": 119000,
            },
        ],
    }

    destino = tmp_path / "factura.pdf"

    renderer = crear_renderer(
        "04_FACTURA_VENTA",
        payload,
        archivo=destino,
    )

    salida = renderer.construir_pdf()

    assert salida.is_file()
    assert salida.stat().st_size > 500


def _payload_comercial_base() -> dict:
    return {
        "numero": "DOC-00001",
        "fecha": "14/08/2026",
        "subtotal": 100000,
        "descuento": 0,
        "impuestos": 19000,
        "total": 119000,
        "total_letras": "CIENTO DIECINUEVE MIL",
        "empresa": {
            "razon_social": "Empresa Demo S.A.S.",
            "nit": "900123456",
            "direccion": "Calle 1",
            "ciudad": "Bogotá",
            "telefono": "6011234567",
        },
        "cliente": {
            "nombre": "Cliente Demo",
            "documento": "800987654",
            "direccion": "Carrera 7",
            "ciudad": "Bogotá",
        },
        "items": [
            {
                "numero": 1,
                "descripcion": "Servicio",
                "cantidad": 1,
                "precio": 100000,
                "descuento": 0,
                "impuestos": 19000,
                "total": 119000,
            },
        ],
    }


def test_crear_renderer_cotizacion(tmp_path):

    payload = {
        **_payload_comercial_base(),
        "fecha_vigencia": "14/09/2026",
        "vendedor": "Ana Pérez",
    }

    destino = tmp_path / "cotizacion.pdf"

    renderer = crear_renderer(
        "01_COTIZACION",
        payload,
        archivo=destino,
    )

    assert renderer.construir_pdf().is_file()


def test_crear_renderer_pedido(tmp_path):

    payload = {
        **_payload_comercial_base(),
        "estado": "Confirmado",
        "vendedor": "Ana Pérez",
    }

    destino = tmp_path / "pedido.pdf"

    renderer = crear_renderer(
        "02_PEDIDO_VENTA",
        payload,
        archivo=destino,
    )

    assert renderer.construir_pdf().is_file()


def test_crear_renderer_recibo_caja(tmp_path):

    payload = {
        "numero": "RC-00001",
        "fecha": "14/08/2026",
        "forma_pago": "Transferencia",
        "valor": 150000,
        "total_letras": "CIENTO CINCUENTA MIL",
        "empresa": _payload_comercial_base()["empresa"],
        "cliente": _payload_comercial_base()["cliente"],
        "lineas": [
            {
                "documento": "Factura FV-001",
                "valor_aplicado": 150000,
                "saldo_anterior": 350000,
                "saldo_restante": 200000,
            },
        ],
    }

    destino = tmp_path / "recibo.pdf"

    renderer = crear_renderer(
        "07_RECIBO_CAJA",
        payload,
        archivo=destino,
    )

    assert renderer.construir_pdf().is_file()


def test_crear_renderer_comprobante_egreso(tmp_path):

    payload = {
        "numero": "CE-00001",
        "fecha": "14/08/2026",
        "forma_pago": "Cheque",
        "valor": 250000,
        "total_letras": "DOSCIENTOS CINCUENTA MIL",
        "empresa": _payload_comercial_base()["empresa"],
        "beneficiario": {
            "nombre": "Proveedor Demo",
            "documento": "800111222-3",
        },
        "lineas": [
            {
                "documento": "FC FC-001",
                "valor_aplicado": 250000,
                "saldo_anterior": 500000,
                "saldo_restante": 250000,
            },
        ],
    }

    destino = tmp_path / "egreso.pdf"

    renderer = crear_renderer(
        "13_COMPROBANTE_EGRESO",
        payload,
        archivo=destino,
    )

    assert renderer.construir_pdf().is_file()


def test_construir_aplicacion_cartera_usa_saldos():

    from aplicacion.documentos.impresion.componentes import (
        construir_aplicacion_cartera,
    )

    bloque = construir_aplicacion_cartera(
        [
            {
                "documento": "Factura FV-001",
                "saldo_anterior": 350000,
                "valor_aplicado": 150000,
                "saldo_restante": 200000,
            },
        ],
    )

    assert len(
        bloque,
    ) == 2


def test_crear_renderer_nota_credito(tmp_path):

    payload = {
        **_payload_comercial_base(),
        "fecha_generacion": "14/08/2026",
        "motivo": "Devolución parcial",
        "factura_referencia": "FV-00001",
        "factura_cufe": "cufe-factura-ref",
    }

    renderer = crear_renderer(
        "05_NOTA_CREDITO",
        payload,
        archivo=tmp_path / "nc.pdf",
    )

    assert renderer.construir_pdf().is_file()


def test_crear_renderer_nota_debito(tmp_path):

    payload = {
        **_payload_comercial_base(),
        "fecha_generacion": "14/08/2026",
        "motivo": "Ajuste al alza",
        "factura_referencia": "FV-00001",
    }

    renderer = crear_renderer(
        "06_NOTA_DEBITO",
        payload,
        archivo=tmp_path / "nd.pdf",
    )

    assert renderer.construir_pdf().is_file()


def test_crear_renderer_remision_logistica(tmp_path):

    payload = {
        "numero": "RM-00001",
        "fecha": "14/08/2026",
        "estado": "despachada",
        "pedido_numero": "PD-00010",
        "empresa": _payload_comercial_base()["empresa"],
        "cliente": _payload_comercial_base()["cliente"],
        "items": [
            {
                "descripcion": "Producto A",
                "cantidad_solicitada": 10,
                "cantidad_entregada": 8,
                "cantidad": 8,
                "unidad": "UND",
            },
        ],
    }

    renderer = crear_renderer(
        "03_REMISION",
        payload,
        archivo=tmp_path / "remision.pdf",
    )

    assert renderer.construir_pdf().is_file()


def test_items_remision_logistica_sin_pedido():

    from aplicacion.reportes.comunes.datos_documento import (
        _items_remision_logistica,
    )

    remision = type(
        "Remision",
        (),
        {"pedido_id": None},
    )()

    detalle = type(
        "Detalle",
        (),
        {
            "descripcion": "Item",
            "cantidad": 5,
            "producto_id": 1,
            "producto_variante_id": None,
        },
    )()

    items = _items_remision_logistica(
        remision,
        [detalle],
    )

    assert items[0]["cantidad_solicitada"] == 5.0
    assert items[0]["cantidad_entregada"] == 5.0
