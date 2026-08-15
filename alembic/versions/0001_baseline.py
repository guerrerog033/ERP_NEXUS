"""Baseline Alembic — esquema ya aplicado vía migraciones.py

Revision ID: 0001_baseline
Revises:
Create Date: 2026-08-09

Las bases existentes deben marcar esta revisión con:

    alembic stamp 0001_baseline

Las nuevas instalaciones pueden seguir usando ``ejecutar_migraciones()``
hasta migrar completamente a revisiones Alembic.
"""

from typing import Sequence, Union

revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
