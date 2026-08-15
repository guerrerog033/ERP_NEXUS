from __future__ import annotations

from pathlib import Path

import pytest

from aplicacion.integraciones.dian.go_live import (
    ValidadorGoLiveDian,
)


def test_verificar_produccion_bloquea_prefijo_setp(
    monkeypatch,
    tmp_path,
):

    certificado = tmp_path / "demo.p12"
    certificado.write_bytes(
        b"demo",
    )

    def _config(
        seccion,
        clave,
        default=None,
    ):

        valores = {
            (
                "dian",
                "emision_habilitada",
            ): True,
            (
                "dian",
                "ambiente_emision",
            ): "produccion",
            (
                "dian",
                "certificado_ruta",
            ): str(
                certificado,
            ),
            (
                "dian",
                "certificado_clave",
            ): "clave-demo",
            (
                "dian",
                "prefijo_factura",
            ): "SETP",
            (
                "dian",
                "test_set_id",
            ): "abc-123",
            (
                "dian",
                "resolucion_numero",
            ): "18760000001",
            (
                "dian",
                "resolucion_fecha_inicio",
            ): "2019-01-19",
            (
                "dian",
                "resolucion_fecha_fin",
            ): "2030-01-19",
            (
                "dian",
                "resolucion_desde",
            ): "990000000",
            (
                "dian",
                "resolucion_hasta",
            ): "995000000",
            (
                "dian",
                "carpeta_xml_venta",
            ): str(
                tmp_path / "xml",
            ),
            (
                "empresa",
                "nit",
            ): "900123456",
            (
                "empresa",
                "nombre",
            ): "Empresa Demo",
        }

        return valores.get(
            (
                seccion,
                clave,
            ),
            default,
        )

    monkeypatch.setattr(
        "aplicacion.integraciones.dian.go_live.Configuracion.obtener",
        _config,
    )

    resultado = ValidadorGoLiveDian.verificar_produccion()

    assert resultado["listo"] is False
    assert any(
        "SETP" in item
        for item in resultado["bloqueantes"]
    )
    assert any(
        "test_set_id" in item
        for item in resultado["bloqueantes"]
    )


def test_verificar_habilitacion_listo_con_setp(
    monkeypatch,
    tmp_path,
):

    certificado = tmp_path / "demo.p12"
    certificado.write_bytes(
        b"demo",
    )

    def _config(
        seccion,
        clave,
        default=None,
    ):

        valores = {
            (
                "dian",
                "emision_habilitada",
            ): True,
            (
                "dian",
                "ambiente_emision",
            ): "habilitacion",
            (
                "dian",
                "certificado_ruta",
            ): str(
                certificado,
            ),
            (
                "dian",
                "certificado_clave",
            ): "clave-demo",
            (
                "dian",
                "prefijo_factura",
            ): "SETP",
            (
                "dian",
                "test_set_id",
            ): "set-demo",
            (
                "dian",
                "resolucion_numero",
            ): "18760000001",
            (
                "dian",
                "resolucion_fecha_inicio",
            ): "2019-01-19",
            (
                "dian",
                "resolucion_fecha_fin",
            ): "2030-01-19",
            (
                "dian",
                "resolucion_desde",
            ): "990000000",
            (
                "dian",
                "resolucion_hasta",
            ): "995000000",
            (
                "dian",
                "carpeta_xml_venta",
            ): str(
                tmp_path / "xml",
            ),
            (
                "empresa",
                "nit",
            ): "900123456",
            (
                "empresa",
                "nombre",
            ): "Empresa Demo",
            (
                "empresa",
                "direccion",
            ): "Calle 1",
            (
                "empresa",
                "ciudad",
            ): "Bogotá",
        }

        return valores.get(
            (
                seccion,
                clave,
            ),
            default,
        )

    monkeypatch.setattr(
        "aplicacion.integraciones.dian.go_live.Configuracion.obtener",
        _config,
    )

    resultado = ValidadorGoLiveDian.verificar_habilitacion()

    assert resultado["listo"] is True
    assert resultado["bloqueantes"] == []


def test_verificar_produccion_falla_sin_certificado(
    monkeypatch,
):

    monkeypatch.setattr(
        "aplicacion.integraciones.dian.go_live.Configuracion.obtener",
        lambda seccion, clave, default=None: {
            (
                "dian",
                "emision_habilitada",
            ): True,
            (
                "dian",
                "ambiente_emision",
            ): "produccion",
            (
                "dian",
                "prefijo_factura",
            ): "FV",
            (
                "dian",
                "resolucion_numero",
            ): "18760000001",
            (
                "dian",
                "resolucion_fecha_inicio",
            ): "2019-01-19",
            (
                "dian",
                "resolucion_fecha_fin",
            ): "2030-01-19",
            (
                "dian",
                "resolucion_desde",
            ): "990000000",
            (
                "dian",
                "resolucion_hasta",
            ): "995000000",
            (
                "empresa",
                "nit",
            ): "900123456",
        }.get(
            (
                seccion,
                clave,
            ),
            default,
        ),
    )

    resultado = ValidadorGoLiveDian.verificar_produccion()

    assert resultado["listo"] is False
    assert any(
        "certificado" in item.lower()
        for item in resultado["bloqueantes"]
    )


def test_resumen_texto_incluye_bloqueantes():

    texto = ValidadorGoLiveDian.resumen_texto(
        {
            "ambiente_objetivo": "produccion",
            "listo": False,
            "bloqueantes": [
                "Falta certificado.",
            ],
            "avisos": [],
        },
    )

    assert "PENDIENTE" in texto
    assert "Falta certificado." in texto
