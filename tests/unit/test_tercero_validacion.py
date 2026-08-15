from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from aplicacion.dominio.documentos.dv import DVCalculator
from aplicacion.maestros.terceros.constantes import (
    CAMPOS_RESPONSABILIDAD_FISCAL,
)
from aplicacion.maestros.terceros.servicio import TerceroServicio


def _datos_tercero_base(**extra):

    datos = {
        "tipo_documento": "CC",
        "numero_documento": "1234567890",
        "tipo_tercero": "Cliente",
        "primer_nombre": "Juan",
        "primer_apellido": "Pérez",
        "direccion": "Calle 1 # 2-3",
        "pais": "Colombia",
        "departamento": "Cundinamarca",
        "ciudad": "Bogotá",
        "correo": "juan@demo.com",
        "dias_credito": 0,
        "cupo_credito": 0,
        "resp_r99_pn": True,
    }

    datos.update(
        extra,
    )

    return datos


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_validar_nit_requiere_razon_social(
    _mock_documento,
):

    datos = _datos_tercero_base(
        tipo_documento="NIT",
        numero_documento="900123456",
        razon_social="",
        primer_nombre="",
        primer_apellido="",
    )

    with pytest.raises(
        ValueError,
        match="razón social",
    ):

        TerceroServicio.validar(
            datos,
        )


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_validar_nit_asigna_dv(
    _mock_documento,
):

    datos = _datos_tercero_base(
        tipo_documento="NIT",
        numero_documento="900123456",
        razon_social="Empresa Demo S.A.S.",
        dv="",
        primer_nombre="",
        primer_apellido="",
    )

    TerceroServicio.validar(
        datos,
    )

    assert datos["dv"] == DVCalculator.calcular(
        "900123456",
    )


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_validar_persona_requiere_nombre_o_razon(
    _mock_documento,
):

    datos = _datos_tercero_base(
        primer_nombre="",
        primer_apellido="",
        razon_social="",
    )

    with pytest.raises(
        ValueError,
        match="primer nombre",
    ):

        TerceroServicio.validar(
            datos,
        )


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_validar_correo_invalido(
    _mock_documento,
):

    datos = _datos_tercero_base(
        correo="correo-invalido",
    )

    with pytest.raises(
        ValueError,
        match="correo",
    ):

        TerceroServicio.validar(
            datos,
        )


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_validar_credito_no_negativo(
    _mock_documento,
):

    datos = _datos_tercero_base(
        dias_credito=-1,
    )

    with pytest.raises(
        ValueError,
        match="días de crédito",
    ):

        TerceroServicio.validar(
            datos,
        )


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_validar_nit_rechaza_dv_incorrecto(
    _mock_documento,
):

    datos = _datos_tercero_base(
        tipo_documento="NIT",
        numero_documento="900123456",
        razon_social="Empresa Demo S.A.S.",
        dv="0",
        primer_nombre="",
        primer_apellido="",
    )

    with pytest.raises(
        ValueError,
        match="dígito de verificación",
    ):

        TerceroServicio.validar(
            datos,
        )


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_validar_responsabilidad_fiscal_default_r99(
    _mock_documento,
):

    datos = _datos_tercero_base()

    for campo in CAMPOS_RESPONSABILIDAD_FISCAL:

        datos[campo] = False

    TerceroServicio.validar(
        datos,
    )

    assert datos["resp_r99_pn"] is True


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_validar_tipo_tercero_invalido(
    _mock_documento,
):

    datos = _datos_tercero_base(
        tipo_tercero="Empleado",
    )

    with pytest.raises(
        ValueError,
        match="tipo de tercero",
    ):

        TerceroServicio.validar(
            datos,
        )


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
)
def test_validar_rechaza_documento_duplicado(
    mock_documento,
):

    mock_documento.return_value = SimpleNamespace(
        id=99,
    )

    datos = _datos_tercero_base()

    with pytest.raises(
        ValueError,
        match="Ya existe",
    ):

        TerceroServicio.validar(
            datos,
        )


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
)
def test_validar_permite_edicion_mismo_documento(
    mock_documento,
):

    mock_documento.return_value = SimpleNamespace(
        id=5,
    )

    datos = _datos_tercero_base()

    TerceroServicio.validar(
        datos,
        id_registro=5,
    )


@patch.object(
    TerceroServicio.repositorio,
    "obtener_por_documento",
    return_value=None,
)
def test_validar_nit_normaliza_solo_digitos(
    _mock_documento,
):

    datos = _datos_tercero_base(
        tipo_documento="NIT",
        numero_documento="900.123.456",
        razon_social="Empresa Demo S.A.S.",
        dv="",
        primer_nombre="",
        primer_apellido="",
    )

    TerceroServicio.validar(
        datos,
    )

    assert datos["numero_documento"] == "900123456"
    assert datos["dv"] == DVCalculator.calcular(
        "900123456",
    )
