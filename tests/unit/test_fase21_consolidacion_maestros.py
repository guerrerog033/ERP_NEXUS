"""Fase 21 — consolidación maestros y trazabilidad documental."""

from __future__ import annotations

import importlib

import pytest

from aplicacion.base_datos.registro_modelos import importar_modelos
from aplicacion.maestros.terceros.constantes import TIPO_A_ROL
from aplicacion.maestros.terceros.servicio import TerceroServicio
from aplicacion.nucleo.documentos.trazabilidad import (
    vincular_cotizacion_pedido,
)


def test_registro_modelos_incluye_fase21():
    importar_modelos()

    modulos = (
        "aplicacion.maestros.unidades_medida.modelos",
        "aplicacion.maestros.formas_pago.modelos",
        "aplicacion.maestros.medios_pago.modelos",
        "aplicacion.maestros.vendedores.modelos",
        "aplicacion.maestros.atributos.modelos",
        "aplicacion.nucleo.documentos.modelos",
        "aplicacion.nucleo.numeracion.modelos",
    )

    for modulo in modulos:
        importlib.import_module(modulo)


def test_sincronizar_roles_desde_tipo_tercero():
    datos = {
        "tipo_tercero": "Cliente",
    }

    TerceroServicio._sincronizar_roles(
        datos,
    )

    assert datos["es_cliente"] is True


def test_tipo_a_rol_cubre_roles_comerciales():
    assert TIPO_A_ROL["Cliente"] == "es_cliente"
    assert TIPO_A_ROL["Proveedor"] == "es_proveedor"
    assert TIPO_A_ROL["Empleado"] == "es_empleado"
    assert TIPO_A_ROL["Vendedor"] == "es_vendedor"


def test_vincular_cotizacion_pedido_idempotente(monkeypatch):
    llamadas: list[tuple] = []

    class _Repo:

        @classmethod
        def registrar(
            cls,
            tipo_origen,
            documento_origen_id,
            tipo_destino,
            documento_destino_id,
        ):
            llamadas.append(
                (
                    tipo_origen,
                    documento_origen_id,
                    tipo_destino,
                    documento_destino_id,
                ),
            )

    monkeypatch.setattr(
        "aplicacion.nucleo.documentos.trazabilidad.DocumentoVinculoRepositorio",
        _Repo,
    )

    vincular_cotizacion_pedido(
        10,
        20,
    )

    assert llamadas == [
        (
            "COTIZACION",
            10,
            "PEDIDO_VENTA",
            20,
        ),
    ]
