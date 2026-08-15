#!/usr/bin/env python3
"""
Verifica la cadena Alembic del ERP NEXUS.

Uso:
    python scripts/ci/verificar_alembic.py
    python scripts/ci/verificar_alembic.py --upgrade
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(
    __file__,
).resolve().parents[2]

if str(
    ROOT,
) not in sys.path:

    sys.path.insert(
        0,
        str(
            ROOT,
        ),
    )


def verificar_cadena() -> str:

    from alembic.config import Config
    from alembic.script import ScriptDirectory

    from aplicacion.base_datos.registro_modelos import (
        importar_modelos,
    )

    importar_modelos()

    config = Config(
        str(
            ROOT / "alembic.ini",
        ),
    )

    script = ScriptDirectory.from_config(
        config,
    )

    heads = script.get_revisions(
        "heads",
    )

    if len(
        heads,
    ) != 1:

        revisiones = [
            revision.revision
            for revision in heads
        ]

        raise RuntimeError(
            "Se esperaba un único head Alembic; "
            f"encontrados: {revisiones}",
        )

    return heads[
        0
    ].revision


def aplicar_migraciones() -> None:

    from alembic import command
    from alembic.config import Config

    config = Config(
        str(
            ROOT / "alembic.ini",
        ),
    )

    command.upgrade(
        config,
        "head",
    )


def main() -> int:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Ejecuta alembic upgrade head",
    )

    args = parser.parse_args()

    head = verificar_cadena()

    print(
        f"Alembic OK — head: {head}",
    )

    if args.upgrade:

        aplicar_migraciones()

        print(
            "Migraciones aplicadas: head",
        )

    return 0


if __name__ == "__main__":

    try:

        raise SystemExit(
            main(),
        )

    except Exception as error:

        print(
            f"Error Alembic: {error}",
            file=sys.stderr,
        )

        raise SystemExit(
            1,
        ) from error
