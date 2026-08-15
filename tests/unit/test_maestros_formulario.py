from __future__ import annotations

from types import SimpleNamespace

import pytest

from aplicacion.framework.form.engine import FormEngine
from aplicacion.maestros.categorias.categoria_definition import (
    CategoriaDefinition,
)
from aplicacion.maestros.empresas.empresa_definition import (
    EmpresaDefinition,
)
from aplicacion.maestros.impuestos.impuesto_definition import (
    ImpuestoDefinition,
)
from aplicacion.maestros.listas_precio.lista_precio_definition import (
    ListaPrecioDefinition,
)
from aplicacion.maestros.marcas.marca_definition import (
    MarcaDefinition,
)


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


MAESTROS_FORM = (
    (
        "marca",
        MarcaDefinition,
        {
            "codigo": "M01",
            "nombre": "Marca Demo",
            "descripcion": "Descripción",
            "activo": True,
        },
    ),
    (
        "categoria",
        CategoriaDefinition,
        {
            "codigo": "CAT01",
            "nombre": "Categoría Demo",
            "descripcion": "Descripción",
            "activo": True,
        },
    ),
    (
        "impuesto",
        ImpuestoDefinition,
        {
            "codigo": "IVA19",
            "nombre": "Iva 19%",
            "porcentaje": 19.0,
            "tipo": "IVA",
            "activo": True,
        },
    ),
    (
        "lista_precio",
        ListaPrecioDefinition,
        {
            "codigo": "LP01",
            "nombre": "Lista General",
            "predeterminada": True,
            "activo": True,
        },
    ),
)


@pytest.mark.parametrize(
    "nombre,definition,datos",
    MAESTROS_FORM,
)
def test_maestro_form_engine_construye_y_binding(
    nombre,
    definition,
    datos,
):
    _qapp()

    engine = FormEngine(
        definition,
    )

    engine.construir()

    assert engine.widget(
        "codigo",
    ) is not None
    assert engine.widget(
        "nombre",
    ) is not None

    engine.cargar(
        SimpleNamespace(
            **datos,
        ),
    )

    valores = engine.valores()

    assert valores["codigo"] == datos["codigo"]
    assert valores["nombre"] == datos["nombre"]
    assert valores["activo"] is True


def test_empresa_form_engine_construye_y_binding():
    _qapp()

    engine = FormEngine(
        EmpresaDefinition,
    )

    engine.construir()

    datos = {
        "nit": "900123456",
        "dv": "7",
        "razon_social": "Empresa Demo S.A.S.",
        "nombre_comercial": "Demo",
        "direccion": "Calle 1",
        "pais": "Colombia",
        "departamento": "Cundinamarca",
        "ciudad": "Bogotá",
        "telefono": "6011234567",
        "celular": "3001234567",
        "correo": "info@demo.com",
        "activo": True,
    }

    for nombre in (
        "nit",
        "razon_social",
        "correo",
        "telefono",
    ):
        assert engine.widget(
            nombre,
        ) is not None

    engine.cargar(
        SimpleNamespace(
            **datos,
        ),
    )

    valores = engine.valores()

    assert valores["nit"] == "900123456"
    assert valores["razon_social"] == "Empresa Demo S.A.S."
    assert valores["correo"] == "info@demo.com"
    assert valores["activo"] is True
