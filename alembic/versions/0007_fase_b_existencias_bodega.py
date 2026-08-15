"""Revisiones Alembic — Fase B: existencias por bodega."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_fase_b_existencias_bodega"
down_revision: Union[str, None] = "0006_fase10_pos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    tablas = set(
        inspector.get_table_names(),
    )

    if (
        "existencias_bodega"
        not in tablas
    ):

        op.create_table(
            "existencias_bodega",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column(
                "bodega_id",
                sa.Integer(),
                sa.ForeignKey(
                    "bodegas.id",
                ),
                nullable=False,
            ),
            sa.Column(
                "producto_id",
                sa.Integer(),
                sa.ForeignKey(
                    "productos.id",
                ),
                nullable=False,
            ),
            sa.Column(
                "producto_variante_id",
                sa.Integer(),
                sa.ForeignKey(
                    "producto_variantes.id",
                ),
                nullable=True,
            ),
            sa.Column(
                "cantidad",
                sa.Numeric(
                    18,
                    4,
                ),
                nullable=False,
                server_default="0",
            ),
        )

        op.create_index(
            "ix_existencias_bodega_bodega",
            "existencias_bodega",
            ["bodega_id"],
        )

        op.create_index(
            "ix_existencias_bodega_producto",
            "existencias_bodega",
            ["producto_id"],
        )

        op.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_existencias_bodega_sin_variante
            ON existencias_bodega (bodega_id, producto_id)
            WHERE producto_variante_id IS NULL
            """
        )

        op.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_existencias_bodega_con_variante
            ON existencias_bodega (bodega_id, producto_id, producto_variante_id)
            WHERE producto_variante_id IS NOT NULL
            """
        )


def downgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    if (
        "existencias_bodega"
        in inspector.get_table_names()
    ):

        op.drop_index(
            "ix_existencias_bodega_producto",
            table_name="existencias_bodega",
        )

        op.drop_index(
            "ix_existencias_bodega_bodega",
            table_name="existencias_bodega",
        )

        op.drop_table(
            "existencias_bodega",
        )
