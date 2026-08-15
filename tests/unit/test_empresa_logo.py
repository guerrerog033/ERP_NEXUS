from __future__ import annotations

from pathlib import Path

import pytest

PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452"
    "00000001000000010802000000907753"
    "de0000000c49444154789c63f8cfc000"
    "0003010100c9fe92ef0000000049454e"
    "44ae426082"
)


@pytest.fixture(autouse=True)
def _ruta_logos_temporal(tmp_path, monkeypatch):

    from aplicacion.maestros.empresas import servicios

    ruta = tmp_path / "empresa"

    monkeypatch.setattr(
        servicios,
        "RUTA_LOGOS",
        ruta,
    )

    return ruta


def _crear_png(tmp_path: Path, nombre: str = "logo.png") -> Path:

    archivo = tmp_path / nombre

    archivo.write_bytes(
        PNG_1X1,
    )

    return archivo


def test_guardar_logo_copia_archivo_y_devuelve_ruta_relativa(
    tmp_path,
):
    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    origen = _crear_png(
        tmp_path,
    )

    resultado = EmpresaServicio._guardar_logo(
        str(origen),
        "900123456",
    )

    assert resultado == "empresa/900123456.png"


def test_guardar_logo_sanea_nit_con_guiones_y_puntos(
    tmp_path,
):
    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    origen = _crear_png(
        tmp_path,
    )

    resultado = EmpresaServicio._guardar_logo(
        str(origen),
        "900.123.456-7",
    )

    assert resultado == "empresa/9001234567.png"


def test_guardar_logo_con_archivo_inexistente_conserva_logo_actual(
    tmp_path,
):
    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    resultado = EmpresaServicio._guardar_logo(
        str(tmp_path / "no_existe.png"),
        "900123456",
        "empresa/anterior.png",
    )

    assert resultado == "empresa/anterior.png"


def test_ruta_logo_absoluta_resuelve_archivo_existente(
    tmp_path,
    _ruta_logos_temporal,
):
    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    _ruta_logos_temporal.mkdir(
        parents=True,
    )

    (
        _ruta_logos_temporal
        / "900123456.png"
    ).write_bytes(
        PNG_1X1,
    )

    ruta = EmpresaServicio.ruta_logo_absoluta(
        "empresa/900123456.png",
    )

    assert ruta is not None
    assert ruta.is_file()


def test_ruta_logo_absoluta_sin_valor_devuelve_none():

    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    assert (
        EmpresaServicio.ruta_logo_absoluta(
            None,
        )
        is None
    )

    assert (
        EmpresaServicio.ruta_logo_absoluta(
            "",
        )
        is None
    )


def test_ruta_logo_absoluta_con_archivo_inexistente_devuelve_none():

    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    assert (
        EmpresaServicio.ruta_logo_absoluta(
            "empresa/no_existe.png",
        )
        is None
    )


def test_validar_procesa_logo_pendiente_y_lo_quita_de_datos(
    tmp_path,
):
    from unittest.mock import patch

    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    origen = _crear_png(
        tmp_path,
    )

    datos = {
        "nit": "900999999",
        "razon_social": "Empresa Logo Demo",
        "_logo_archivo": str(origen),
    }

    with patch.object(
        EmpresaServicio.repositorio,
        "obtener_por_nit",
        return_value=None,
    ):

        EmpresaServicio.validar(
            datos,
        )

    assert "_logo_archivo" not in datos
    assert datos["logo_ruta"] == "empresa/900999999.png"


def test_validar_sin_logo_pendiente_no_agrega_logo_ruta():

    from unittest.mock import patch

    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    datos = {
        "nit": "900999998",
        "razon_social": "Empresa Sin Logo",
    }

    with patch.object(
        EmpresaServicio.repositorio,
        "obtener_por_nit",
        return_value=None,
    ):

        EmpresaServicio.validar(
            datos,
        )

    assert "logo_ruta" not in datos
