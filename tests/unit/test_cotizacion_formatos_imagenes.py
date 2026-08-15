from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest

from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    _GENERADORES,
    ContextoFormato,
)


def _contexto(
    *,
    mostrar_imagenes: bool,
    etiqueta_contraparte: str = "Cliente",
) -> ContextoFormato:

    detalle = SimpleNamespace(
        producto_id=None,
        descripcion="Servicio de prueba",
        cantidad=1,
        precio_unitario=1000,
        impuesto_id=None,
        total_linea=1000,
    )

    return ContextoFormato(
        cotizacion=SimpleNamespace(
            numero="0001",
            fecha=date(2026, 8, 15),
        ),
        detalles=[detalle],
        nombre_cliente="Contraparte de prueba",
        resumen={
            "subtotal": 1000,
            "retefuente": 0,
            "reteica": 0,
            "reteiva": 0,
            "iva": 0,
            "total": 1000,
        },
        empresa={
            "nombre": "Empresa Demo",
            "nit": "900123456",
            "direccion": "",
            "telefono": "",
            "correo": "",
            "ciudad": "",
            "pais": "Colombia",
            "notas_pie": "",
            "vendedor_nombre": "",
            "vendedor_correo": "",
            "vendedor_telefono": "",
            "logo_ruta": "",
        },
        cliente={
            "nombre": "Contraparte de prueba",
            "nit": "",
            "contacto": "Contraparte de prueba",
            "direccion": "No aplica",
            "ciudad": "",
            "telefono": "",
            "correo": "",
        },
        fecha="2026-08-15",
        observaciones="",
        mostrar_imagenes=mostrar_imagenes,
        etiqueta_contraparte=etiqueta_contraparte,
    )


FORMATOS_CON_IMAGEN = (
    "carta",
    "corporativo",
    "moderno",
    "compacto",
    "estandar",
)


@pytest.mark.parametrize(
    "codigo",
    FORMATOS_CON_IMAGEN,
)
def test_mostrar_imagenes_false_no_incluye_columna_de_imagen(
    codigo,
):
    """
    Regresión: carta/corporativo/moderno/compacto llamaban a
    _imagen_html() sin condición, ignorando ctx.mostrar_imagenes.
    Facturas/Pedidos/Remisiones ya pasaban mostrar_imagenes=False
    sin que tuviera ningún efecto en estos 4 formatos.
    """
    generador = _GENERADORES[codigo]

    html = generador(
        _contexto(
            mostrar_imagenes=False,
        ),
    )

    assert "background:#f8fafc;border:1px solid #e2e8f0" not in html
    assert "<img " not in html


@pytest.mark.parametrize(
    "codigo",
    FORMATOS_CON_IMAGEN,
)
def test_mostrar_imagenes_true_conserva_columna_de_imagen(
    codigo,
):
    generador = _GENERADORES[codigo]

    html = generador(
        _contexto(
            mostrar_imagenes=True,
        ),
    )

    assert "background:#f8fafc;border:1px solid #e2e8f0" in html


def test_tirilla_nunca_muestra_imagen():

    generador = _GENERADORES["tirilla"]

    for mostrar in (True, False):

        html = generador(
            _contexto(
                mostrar_imagenes=mostrar,
            ),
        )

        assert "background:#f8fafc;border:1px solid #e2e8f0" not in html
        assert "<img " not in html


@pytest.mark.parametrize(
    "codigo",
    (
        "carta",
        "corporativo",
        "moderno",
        "compacto",
        "tirilla",
    ),
)
def test_etiqueta_contraparte_personalizada_reemplaza_cliente(
    codigo,
):
    """
    Regresión: "Cliente" estaba hardcodeado en 4 de los 6 formatos,
    lo que impedía reusarlos para documentos con contraparte
    "Proveedor" (Compras) sin decir "Cliente" en una orden de compra.
    """
    generador = _GENERADORES[codigo]

    html = generador(
        _contexto(
            mostrar_imagenes=False,
            etiqueta_contraparte="Proveedor",
        ),
    )

    assert "Cliente" not in html
    assert "Proveedor" in html


def test_etiqueta_contraparte_por_defecto_sigue_siendo_cliente():

    for codigo in (
        "carta",
        "corporativo",
        "moderno",
        "compacto",
        "tirilla",
    ):

        generador = _GENERADORES[codigo]

        html = generador(
            _contexto(
                mostrar_imagenes=False,
            ),
        )

        assert "Cliente" in html
