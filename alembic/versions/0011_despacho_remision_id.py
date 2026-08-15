"""Revisiones Alembic — remision_id en despachos."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0011_despacho_remision_id"
down_revision: Union[str, None] = "0010_guias_remision_electronica"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    columnas = {
        col["name"]
        for col in inspector.get_columns(
            "despachos_pedido",
        )
    }

    if "remision_id" not in columnas:

        op.add_column(
            "despachos_pedido",
            sa.Column(
                "remision_id",
                sa.Integer(),
                sa.ForeignKey(
                    "remisiones_venta.id",
                ),
            ),
        )

        op.create_index(
            "ix_despacho_remision_id",
            "despachos_pedido",
            ["remision_id"],
        )


def downgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    columnas = {
        col["name"]
        for col in inspector.get_columns(
            "despachos_pedido",
        )
    }

    if "remision_id" in columnas:

        op.drop_index(
            "ix_despacho_remision_id",
            table_name="despachos_pedido",
        )

        op.drop_column(
            "despachos_pedido",
            "remision_id",
        )
