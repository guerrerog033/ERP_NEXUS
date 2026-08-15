"""Fase 17 — saneamiento arquitectónico (legacy ausente + reglas de capas)."""

from __future__ import annotations

import ast
from pathlib import Path

import scripts.ci.inventario_codigo_muerto as inventario


def test_inventario_codigo_muerto_ok():
    assert inventario.main() == 0


def test_registro_modelos_es_punto_unico_orm():
    raiz = Path(__file__).resolve().parents[2]
    main = (raiz / "main.py").read_text(encoding="utf-8")
    assert "importar_modelos" in main
    assert "base_datos.modelos" not in main


def test_comunes_sin_ui_legacy():
    raiz = Path(__file__).resolve().parents[2]
    comunes = raiz / "aplicacion" / "comunes"

    permitidos = {
        "__init__.py",
        "auditoria_documento.py",
        "controlador_base.py",
        "exportacion.py",
        "qr_util.py",
        "repositorio_base.py",
        "servicio_base.py",
        "transaccion.py",
    }

    archivos = {
        p.name
        for p in comunes.glob("*.py")
        if p.is_file()
    }

    assert archivos == permitidos


def test_main_no_importa_modelos_parciales():
    raiz = Path(__file__).resolve().parents[2]
    arbol = ast.parse((raiz / "main.py").read_text(encoding="utf-8"))

    modulos = {
        nodo.module
        for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.ImportFrom) and nodo.module
    }

    assert not any(
        modulo.startswith("aplicacion.maestros.")
        or modulo.startswith("aplicacion.modulos.")
        for modulo in modulos
    )
