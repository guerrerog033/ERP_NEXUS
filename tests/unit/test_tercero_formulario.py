from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from aplicacion.dominio.documentos.resultado import DocumentoResult
from aplicacion.framework.form.engine import FormEngine
from aplicacion.maestros.terceros.formulario import TerceroFormulario
from aplicacion.maestros.terceros.servicio import TerceroServicio
from aplicacion.maestros.terceros.terceros_definition import (
    TerceroDefinition,
)


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


@contextmanager
def _patch_retenciones():
    with patch(
        "aplicacion.maestros.impuestos.servicios.ServicioImpuesto.inicializar_predeterminados",
    ), patch(
        "aplicacion.maestros.impuestos.retenciones_catalogo.opciones_retencion_combo",
        return_value=[],
    ):
        yield


def _tercero_mock(**extra):
    datos = {
        "tipo_documento": "CC",
        "numero_documento": "1234567890",
        "tipo_tercero": "Cliente",
        "primer_nombre": "Ana",
        "primer_apellido": "López",
        "direccion": "Calle 10 # 20-30",
        "pais": "Colombia",
        "departamento": "Antioquia",
        "ciudad": "Medellín",
        "correo": "ana@demo.com",
        "telefono": "6041234567",
        "celular": "3001234567",
        "dias_credito": 30,
        "cupo_credito": 1000000,
        "activo": True,
    }

    datos.update(
        extra,
    )

    return SimpleNamespace(
        **datos,
    )


def test_tercero_form_engine_construye_campos_clave():
    _qapp()

    engine = FormEngine(
        TerceroDefinition,
    )

    engine.construir()

    for nombre in (
        "tipo_documento",
        "numero_documento",
        "tipo_tercero",
        "primer_nombre",
        "correo",
        "telefono",
        "celular",
    ):
        assert engine.widget(
            nombre,
        ) is not None


def test_tercero_form_engine_binding_carga_y_exporta():
    _qapp()

    engine = FormEngine(
        TerceroDefinition,
    )

    engine.construir()

    engine.cargar(
        _tercero_mock(),
    )

    valores = engine.valores()

    assert valores["tipo_documento"] == "CC"
    assert valores["numero_documento"] == "1234567890"
    assert valores["primer_nombre"] == "Ana"
    assert valores["correo"] == "ana@demo.com"
    assert valores["telefono"] == "6041234567"
    assert valores["celular"] == "3001234567"
    assert valores["activo"] is True


@_patch_retenciones()
def test_tercero_formulario_modo_nuevo_tipo_tercero_inicial():
    _qapp()

    form = TerceroFormulario(
        tipo_tercero_inicial="Proveedor",
    )

    assert form.engine is not None
    assert form.formulario.binding.valor(
        "tipo_tercero",
    ) == "Proveedor"


@_patch_retenciones()
@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_tercero_formulario_validacion_integrada_servicio(
    _mock_documento,
):
    _qapp()

    form = TerceroFormulario()

    binding = form.formulario.binding

    binding.set_valor(
        "tipo_documento",
        "CC",
    )
    binding.set_valor(
        "numero_documento",
        "9876543210",
    )
    binding.set_valor(
        "tipo_tercero",
        "Cliente",
    )
    binding.set_valor(
        "primer_nombre",
        "Carlos",
    )
    binding.set_valor(
        "primer_apellido",
        "Ruiz",
    )
    binding.set_valor(
        "direccion",
        "Carrera 50 # 80-10",
    )
    binding.set_valor(
        "pais",
        "Colombia",
    )
    binding.set_valor(
        "departamento",
        "Cundinamarca",
    )
    binding.set_valor(
        "ciudad",
        "Bogotá",
    )
    binding.set_valor(
        "correo",
        "carlos@demo.com",
    )
    binding.set_valor(
        "dias_credito",
        0,
    )
    binding.set_valor(
        "cupo_credito",
        0,
    )

    datos = binding.valores()

    TerceroServicio.validar(
        datos,
    )

    assert datos["numero_documento"] == "9876543210"
    assert datos["correo"] == "carlos@demo.com"


@_patch_retenciones()
@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_tercero_formulario_validacion_integrada_rechaza_correo(
    _mock_documento,
):
    _qapp()

    form = TerceroFormulario()

    binding = form.formulario.binding

    binding.set_valor(
        "tipo_documento",
        "CC",
    )
    binding.set_valor(
        "numero_documento",
        "1111111111",
    )
    binding.set_valor(
        "tipo_tercero",
        "Cliente",
    )
    binding.set_valor(
        "primer_nombre",
        "Test",
    )
    binding.set_valor(
        "primer_apellido",
        "Usuario",
    )
    binding.set_valor(
        "correo",
        "correo-invalido",
    )

    with pytest.raises(
        ValueError,
        match="correo",
    ):
        TerceroServicio.validar(
            binding.valores(),
        )


@_patch_retenciones()
def test_tipo_documento_changed_limpia_dv():
    _qapp()

    form = TerceroFormulario()

    binding = form.formulario.binding

    binding.set_valor(
        "tipo_documento",
        "NIT",
    )
    binding.set_valor(
        "dv",
        "7",
    )

    form._tipo_documento_changed()

    assert binding.valor(
        "dv",
    ) == ""


@_patch_retenciones()
@patch.object(
    TerceroFormulario,
    "mostrar_info",
)
@patch.object(
    TerceroFormulario,
    "mostrar_error",
)
def test_documento_changed_limpia_campos_si_numero_vacio(
    _mock_error,
    _mock_info,
):
    _qapp()

    form = TerceroFormulario()

    binding = form.formulario.binding

    binding.set_valor(
        "primer_nombre",
        "Temporal",
    )
    binding.set_valor(
        "correo",
        "temp@demo.com",
    )
    binding.set_valor(
        "numero_documento",
        "",
    )

    form._documento_changed()

    assert binding.valor(
        "primer_nombre",
    ) == ""
    assert binding.valor(
        "correo",
    ) == ""


@_patch_retenciones()
@patch.object(
    TerceroFormulario,
    "mostrar_info",
)
@patch.object(
    TerceroFormulario,
    "mostrar_error",
)
def test_documento_changed_aplica_datos_externos_nit(
    _mock_error,
    _mock_info,
):
    _qapp()

    form = TerceroFormulario()

    resultado = DocumentoResult(
        tipo="NIT",
        numero="900123456",
        dv="7",
        razon_social="Empresa Externa S.A.S.",
        nombre_comercial="Empresa Externa",
        direccion="Carrera 7 # 71-21",
        ciudad="Bogotá",
        departamento="Cundinamarca",
        correo="contacto@externa.com",
    )

    with patch.object(
        form.datasource,
        "documento_changed",
        return_value=resultado,
    ):
        form.formulario.set_valor(
            "tipo_documento",
            "NIT",
        )
        form.formulario.set_valor(
            "numero_documento",
            "900123456",
        )

        form._documento_changed()

    binding = form.formulario.binding

    assert binding.valor(
        "dv",
    ) == "7"
    assert binding.valor(
        "razon_social",
    ) == "Empresa Externa S.A.S."
    assert binding.valor(
        "primer_nombre",
    ) == ""
    assert binding.valor(
        "correo",
    ) == "contacto@externa.com"
    _mock_info.assert_called_once()


@_patch_retenciones()
@patch.object(
    TerceroFormulario,
    "mostrar_info",
)
@patch.object(
    TerceroFormulario,
    "mostrar_error",
)
def test_documento_changed_aplica_datos_externos_persona(
    _mock_error,
    _mock_info,
):
    _qapp()

    form = TerceroFormulario()

    resultado = DocumentoResult(
        tipo="CC",
        numero="1234567890",
        dv="",
        primer_nombre="María",
        primer_apellido="Gómez",
        direccion="Calle 10",
        ciudad="Medellín",
        correo="maria@demo.com",
    )

    with patch.object(
        form.datasource,
        "documento_changed",
        return_value=resultado,
    ):
        form.formulario.set_valor(
            "tipo_documento",
            "CC",
        )
        form.formulario.set_valor(
            "numero_documento",
            "1234567890",
        )

        form._documento_changed()

    binding = form.formulario.binding

    assert binding.valor(
        "primer_nombre",
    ) == "María"
    assert binding.valor(
        "primer_apellido",
    ) == "Gómez"
    assert binding.valor(
        "razon_social",
    ) == ""
    assert binding.valor(
        "pais",
    ) == "Colombia"


@_patch_retenciones()
def test_distribuir_nombre_persona_cuatro_partes():
    _qapp()

    form = TerceroFormulario()

    form._distribuir_nombre_persona(
        "Juan Carlos Pérez López",
    )

    binding = form.formulario.binding

    assert binding.valor(
        "primer_nombre",
    ) == "Juan"
    assert binding.valor(
        "segundo_nombre",
    ) == "Carlos"
    assert binding.valor(
        "primer_apellido",
    ) == "Pérez"
    assert binding.valor(
        "segundo_apellido",
    ) == "López"


@patch(
    "aplicacion.maestros.impuestos.servicios.ServicioImpuesto.inicializar_predeterminados",
)
@patch(
    "aplicacion.maestros.impuestos.retenciones_catalogo.opciones_retencion_combo",
    return_value=[
        (
            "— Sin retención —",
            None,
        ),
        (
            "Retefuente 2.5%",
            1,
        ),
    ],
)
def test_preparar_campos_retencion_carga_opciones(
    _mock_opciones,
    _mock_impuesto,
):
    form = TerceroFormulario.__new__(
        TerceroFormulario,
    )
    form.es_edicion = False
    form.definition = TerceroDefinition

    form._preparar_campos_retencion()

    campo = TerceroDefinition.buscar_campo(
        "retefuente_id",
    )

    assert campo is not None
    assert len(
        campo.opciones,
    ) >= 2
    assert campo.opciones[1][0] == "Retefuente 2.5%"
    assert campo.opciones[1][1] == 1


@_patch_retenciones()
@patch.object(
    TerceroFormulario,
    "mostrar_info",
)
@patch.object(
    TerceroFormulario,
    "mostrar_error",
)
def test_documento_changed_carga_tercero_existente(
    _mock_error,
    _mock_info,
):
    _qapp()

    form = TerceroFormulario()

    tercero = SimpleNamespace(
        tipo_documento="CC",
        numero_documento="5555555555",
        dv="",
        tipo_tercero="Cliente",
        primer_nombre="Existente",
        primer_apellido="Usuario",
        razon_social="",
        correo="existente@demo.com",
        activo=True,
    )

    resultado = DocumentoResult(
        tipo="CC",
        numero="5555555555",
        dv="",
        existe=True,
        tercero=tercero,
    )

    with patch.object(
        form.datasource,
        "documento_changed",
        return_value=resultado,
    ):
        form.formulario.set_valor(
            "tipo_documento",
            "CC",
        )
        form.formulario.set_valor(
            "numero_documento",
            "5555555555",
        )

        form._documento_changed()

    binding = form.formulario.binding

    assert binding.valor(
        "primer_nombre",
    ) == "Existente"
    assert binding.valor(
        "correo",
    ) == "existente@demo.com"
    _mock_info.assert_called_once()
