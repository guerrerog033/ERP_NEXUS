#!/usr/bin/env python3
"""Verifica que módulos legacy eliminados no vuelvan al árbol (Fase 12 + 17)."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

RUTAS_PROHIBIDAS = [
    "aplicacion/interfaz/estilos.py",
    "aplicacion/framework/controles",
    "aplicacion/framework/kernel",
    "aplicacion/framework/formulario_crud.py",
    "aplicacion/framework/maestro_crud.py",
    "aplicacion/framework/navegacion.py",
    "aplicacion/base_datos/modelos.py",
    "aplicacion/maestros/terceros/entidad.py",
    "aplicacion/comunes/maestro_base.py",
    "aplicacion/comunes/formulario_base.py",
    "init_db.py",
]

IMPORTS_PROHIBIDOS = frozenset(
    {
        "aplicacion.base_datos.modelos",
        "aplicacion.comunes.maestro_base",
        "aplicacion.comunes.formulario_base",
    },
)

CARPETAS_IGNORADAS = frozenset(
    {
        ".venv",
        ".git",
        "__pycache__",
        ".pytest_cache",
        "build",
        "dist",
    },
)


def _rutas_python() -> list[Path]:
    archivos: list[Path] = []
    for ruta in RAIZ.rglob("*.py"):
        if any(parte in CARPETAS_IGNORADAS for parte in ruta.parts):
            continue
        archivos.append(ruta)
    return archivos


def _imports_en_archivo(ruta: Path) -> set[str]:
    try:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=str(ruta))
    except SyntaxError:
        return set()

    encontrados: set[str] = set()

    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                encontrados.add(alias.name)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            encontrados.add(nodo.module)

    return encontrados


def verificar_rutas() -> list[str]:
    errores: list[str] = []

    for relativa in RUTAS_PROHIBIDAS:
        ruta = RAIZ / relativa.replace("/", "\\")
        if ruta.exists():
            errores.append(f"Legacy presente: {relativa}")

    return errores


def verificar_imports() -> list[str]:
    errores: list[str] = []

    for ruta in _rutas_python():
        imports = _imports_en_archivo(ruta)
        for prohibido in IMPORTS_PROHIBIDOS & imports:
            relativa = ruta.relative_to(RAIZ).as_posix()
            errores.append(f"Import legacy en {relativa}: {prohibido}")

    return errores


def main() -> int:
    errores = verificar_rutas() + verificar_imports()

    if errores:
        for msg in errores:
            print(msg, file=sys.stderr)
        return 1

    print("Inventario código muerto: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
