"""Fase 1 — cuentas bancarias múltiples por tercero."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0015_tercero_cuentas_bancarias"
down_revision: Union[str, None] = "0014_producto_inventario"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tablas() -> set[str]:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    return set(
        inspector.get_table_names(),
    )


def upgrade() -> None:

    if "tercero_cuentas_bancarias" in _tablas():

        return

    op.create_table(
        "tercero_cuentas_bancarias",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "tercero_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "banco",
            sa.String(length=120),
            nullable=False,
        ),
        sa.Column(
            "tipo_cuenta",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "numero_cuenta",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "titular",
            sa.String(length=200),
            nullable=True,
        ),
        sa.Column(
            "principal",
            sa.Boolean(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tercero_id"],
            ["terceros.id"],
        ),
        sa.PrimaryKeyConstraint(
            "id",
        ),
    )


def downgrade() -> None:

    if "tercero_cuentas_bancarias" not in _tablas():

        return

    op.drop_table(
        "tercero_cuentas_bancarias",
    )
