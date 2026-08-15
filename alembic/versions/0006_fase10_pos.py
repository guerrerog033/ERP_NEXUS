"""Revisiones Alembic — Fase 10: cierre caja POS y stock_minimo."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_fase10_pos"
down_revision: Union[str, None] = "0005_numeric_fase6"
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
        "productos"
        in tablas
    ):

        columnas = {
            col["name"]
            for col in inspector.get_columns(
                "productos",
            )
        }

        if (
            "stock_minimo"
            not in columnas
        ):

            op.add_column(
                "productos",
                sa.Column(
                    "stock_minimo",
                    sa.Float(),
                    nullable=False,
                    server_default="0",
                ),
            )

    if (
        "pos_cierres_caja"
        not in tablas
    ):

        op.create_table(
            "pos_cierres_caja",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column(
                "fecha",
                sa.Date(),
                nullable=False,
            ),
            sa.Column(
                "usuario",
                sa.String(
                    50,
                ),
                nullable=False,
                server_default="sistema",
            ),
            sa.Column(
                "efectivo_esperado",
                sa.Numeric(
                    18,
                    2,
                ),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "efectivo_contado",
                sa.Numeric(
                    18,
                    2,
                ),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "diferencia",
                sa.Numeric(
                    18,
                    2,
                ),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "total_ventas",
                sa.Numeric(
                    18,
                    2,
                ),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "ventas_count",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "observaciones",
                sa.Text(),
            ),
            sa.Column(
                "fecha_cierre",
                sa.DateTime(
                    timezone=True,
                ),
                server_default=sa.text(
                    "now()",
                ),
            ),
        )

        op.create_index(
            "ix_pos_cierres_caja_fecha",
            "pos_cierres_caja",
            ["fecha"],
        )


def downgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    tablas = set(
        inspector.get_table_names(),
    )

    if (
        "pos_cierres_caja"
        in tablas
    ):

        op.drop_index(
            "ix_pos_cierres_caja_fecha",
            table_name="pos_cierres_caja",
        )
        op.drop_table(
            "pos_cierres_caja",
        )

    if (
        "productos"
        in tablas
    ):

        columnas = {
            col["name"]
            for col in inspector.get_columns(
                "productos",
            )
        }

        if (
            "stock_minimo"
            in columnas
        ):

            op.drop_column(
                "productos",
                "stock_minimo",
            )
