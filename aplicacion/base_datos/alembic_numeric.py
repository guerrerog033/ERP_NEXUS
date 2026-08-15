"""Utilidades compartidas para revisiones Alembic numeric."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


def alterar_si_existe(
    tabla: str,
    columna: str,
    tipo: sa.types.TypeEngine,
    *,
    using: str,
) -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    if tabla not in inspector.get_table_names():

        return

    columnas = {
        col["name"]
        for col in inspector.get_columns(
            tabla,
        )
    }

    if columna not in columnas:

        return

    op.alter_column(
        tabla,
        columna,
        type_=tipo,
        postgresql_using=using,
    )


def alterar_numeric(
    tablas: dict[str, list[str]],
    precision: int,
    escala: int,
) -> None:

    for tabla, columnas in tablas.items():

        for columna in columnas:

            alterar_si_existe(
                tabla,
                columna,
                sa.Numeric(
                    precision,
                    escala,
                ),
                using=(
                    f"{columna}::numeric({precision},{escala})"
                ),
            )
