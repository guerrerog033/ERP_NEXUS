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
    """
    Reproduce el arranque real de la app (ver
    aplicacion.base_datos.alembic_bridge.aplicar_esquema): primero
    ``Base.metadata.create_all()`` crea el esquema completo desde los
    modelos (orden de FKs resuelto por SQLAlchemy). Sobre una base
    recién creada no queda ningún DDL pendiente por "revisión" —
    replay literal de ``alembic upgrade head`` fallaría con "la
    tabla ya existe" — así que solo se marca ``alembic_version`` en
    head con ``stamp``. Validar únicamente "alembic upgrade head"
    contra una base vacía no es representativo: la cadena de
    revisiones asume un baseline ya aplicado (ver 0001_baseline).
    """

    from aplicacion.base_datos.conexion import Base, engine

    Base.metadata.create_all(
        bind=engine,
    )

    from alembic import command
    from alembic.config import Config
    from alembic.runtime.migration import MigrationContext

    config = Config(
        str(
            ROOT / "alembic.ini",
        ),
    )

    with engine.connect() as conexion:

        revision_actual = MigrationContext.configure(
            conexion,
        ).get_current_revision()

    if revision_actual is None:

        command.stamp(
            config,
            "head",
        )

    else:

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
