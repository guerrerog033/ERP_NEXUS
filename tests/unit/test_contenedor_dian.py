from __future__ import annotations

import zipfile
from datetime import date
from io import BytesIO
from unittest.mock import MagicMock, patch

import requests

from aplicacion.integraciones.dian.cliente_emision import (
    ClienteEmisionDian,
)
from aplicacion.integraciones.dian.contenedor_electronico import (
    adjuntos_contenedor_factura_venta,
)
from aplicacion.integraciones.dian.representacion_grafica import (
    adjunto_pdf_contenedor,
)


def test_crear_zip_incluye_pdf_en_contenedor_local():

    xml = "<Invoice/>"

    pdf = b"%PDF-1.4 test"

    zip_bytes, nombre = ClienteEmisionDian._crear_zip(
        "FV_123.xml",
        xml,
        adjuntos=[
            (
                "FV_123.pdf",
                pdf,
            ),
        ],
    )

    assert nombre == "FV_123.zip"

    with zipfile.ZipFile(
        BytesIO(
            zip_bytes,
        ),
    ) as archivo:

        nombres = archivo.namelist()

        assert "FV_123.xml" in nombres
        assert "FV_123.pdf" in nombres
        assert archivo.read(
            "FV_123.pdf",
        ) == pdf


def test_zip_transmision_dian_solo_xml():

    xml = "<Invoice/>"

    zip_bytes, _ = ClienteEmisionDian._crear_zip(
        "FV_123.xml",
        xml,
    )

    with zipfile.ZipFile(
        BytesIO(
            zip_bytes,
        ),
    ) as archivo:

        assert archivo.namelist() == [
            "FV_123.xml",
        ]


@patch(
    "aplicacion.integraciones.dian.cliente_emision.requests.post",
    side_effect=requests.RequestException("sin red"),
)
@patch(
    "aplicacion.integraciones.dian.cliente_emision.Configuracion.obtener",
    side_effect=lambda seccion, clave, default=None: {
        (
            "dian",
            "emision_habilitada",
        ): True,
    }.get(
        (
            seccion,
            clave,
        ),
        default,
    ),
)
def test_enviar_guarda_contenedor_con_pdf_cuando_habilitado(
    _mock_config,
    _mock_post,
    tmp_path,
    monkeypatch,
):

    capturado: dict = {}

    def _guardar(
        _nombre,
        contenido,
    ):

        ruta = tmp_path / "contenedor.zip"
        ruta.write_bytes(
            contenido,
        )
        capturado["bytes"] = contenido

        return str(
            ruta,
        )

    monkeypatch.setattr(
        ClienteEmisionDian,
        "_guardar_zip_local",
        _guardar,
    )

    pdf = b"%PDF-1.4 demo"

    with patch.object(
        ClienteEmisionDian,
        "_contenedor_incluye_pdf",
        return_value=True,
    ):

        resultado = ClienteEmisionDian.enviar(
            nombre_xml="FV_001.xml",
            xml_firmado="<Invoice/>",
            adjuntos_contenedor=[
                (
                    "FV_001.pdf",
                    pdf,
                ),
            ],
        )

    assert resultado.ruta_zip

    with zipfile.ZipFile(
        resultado.ruta_zip,
    ) as archivo:

        assert "FV_001.xml" in archivo.namelist()
        assert "FV_001.pdf" in archivo.namelist()

    zip_transmision, _ = ClienteEmisionDian._crear_zip(
        "FV_001.xml",
        "<Invoice/>",
    )

    assert zipfile.ZipFile(
        BytesIO(
            zip_transmision,
        ),
    ).namelist() == [
        "FV_001.xml",
    ]


def test_adjunto_pdf_contenedor_usa_mismo_stem():

    nombre, contenido = adjunto_pdf_contenedor(
        "NC_001_abc123.xml",
        b"%PDF",
    )

    assert nombre == "NC_001_abc123.pdf"
    assert contenido == b"%PDF"


@patch(
    "aplicacion.integraciones.dian.contenedor_electronico.pdf_factura_electronica_venta",
    return_value=b"%PDF-1.4 factura",
)
def test_adjuntos_contenedor_factura(
    _mock_pdf,
):

    factura = MagicMock()

    adjuntos = adjuntos_contenedor_factura_venta(
        factura,
        nombre_xml="FV_001_cufe.xml",
        cufe="abc123",
    )

    assert adjuntos is not None
    assert adjuntos[0][0] == "FV_001_cufe.pdf"
    assert adjuntos[0][1].startswith(
        b"%PDF",
    )


@patch(
    "aplicacion.integraciones.dian.contenedor_electronico.pdf_guia_remision_electronica",
    return_value=b"%PDF-1.4 guia",
)
def test_adjuntos_contenedor_guia_remision(
    _mock_pdf,
):

    from aplicacion.integraciones.dian.contenedor_electronico import (
        adjuntos_contenedor_guia_remision,
    )

    guia = MagicMock()

    adjuntos = adjuntos_contenedor_guia_remision(
        guia,
        nombre_xml="GR_001_cude.xml",
        cude="cude123",
    )

    assert adjuntos is not None
    assert adjuntos[0][0] == "GR_001_cude.pdf"


@patch(
    "aplicacion.integraciones.dian.contenedor_electronico.pdf_documento_soporte",
    return_value=b"%PDF-1.4 soporte",
)
def test_adjuntos_contenedor_documento_soporte(
    _mock_pdf,
):

    from aplicacion.integraciones.dian.contenedor_electronico import (
        adjuntos_contenedor_documento_soporte,
    )

    documento = MagicMock()

    adjuntos = adjuntos_contenedor_documento_soporte(
        documento,
        nombre_xml="DS_001_cuds.xml",
        cuds="cuds123",
    )

    assert adjuntos is not None
    assert adjuntos[0][0] == "DS_001_cuds.pdf"


@patch(
    "aplicacion.integraciones.dian.contenedor_electronico.pdf_nomina_electronica",
    return_value=b"%PDF-1.4 nomina",
)
def test_adjuntos_contenedor_nomina_electronica(
    _mock_pdf,
):

    from aplicacion.integraciones.dian.contenedor_electronico import (
        adjuntos_contenedor_nomina_electronica,
    )

    periodo = MagicMock()
    periodo.id = 1

    adjuntos = adjuntos_contenedor_nomina_electronica(
        periodo,
        nombre_xml="NE_202608_NE202608.xml",
        cune="cune123",
        numero="NE202608",
        totales={
            "neto": 1000000,
        },
        trabajadores=[],
    )

    assert adjuntos is not None
    assert adjuntos[0][0] == "NE_202608_NE202608.pdf"


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
    "aplicacion.integraciones.dian.representacion_grafica._nombre_tercero",
    return_value="Cliente XYZ S.A.S.",
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
def test_pdf_factura_electronica_bytes(
    *_mocks,
):

    from aplicacion.integraciones.dian.representacion_grafica import (
        pdf_factura_electronica_venta,
    )

    factura = MagicMock()
    factura.numero = "FV-00001234"
    factura.fecha = date(
        2026,
        8,
        10,
    )
    factura.fecha_vencimiento = None
    factura.fecha_creacion = None
    factura.subtotal = 180000
    factura.iva = 32300
    factura.total = 202300
    factura.estado_pago = "credito"
    factura.cufe = ""
    factura.estado_dian = "Aceptada"
    factura.observaciones = ""
    factura.cliente_id = 1
    factura.consecutivo_dian = "990000001"
    factura.detalles = []

    detalle = MagicMock()
    detalle.descripcion = "Producto A"
    detalle.cantidad = 1
    detalle.precio_unitario = 180000
    detalle.total_linea = 180000
    detalle.impuesto_id = None
    detalle.producto_id = None
    detalle.precio_incluye_iva = False
    detalle.descuento = 0
    factura.detalles = [
        detalle,
    ]

    pdf = pdf_factura_electronica_venta(
        factura,
        cufe="a1b2c3d4e5f6789012345678901234567890abcd",
    )

    assert pdf[:4] == b"%PDF"
    assert len(
        pdf,
    ) > 500
