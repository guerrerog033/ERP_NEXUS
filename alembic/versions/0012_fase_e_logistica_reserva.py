"""Revisiones Alembic — Fase E logística y reserva pedido."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0012_fase_e_logistica_reserva"
down_revision: Union[str, None] = "0011_despacho_remision_id"
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

    if "existencias_bodega" in tablas:

        columnas = {
            col["name"]
            for col in inspector.get_columns(
                "existencias_bodega",
            )
        }

        if "cantidad_reservada" not in columnas:

            op.add_column(
                "existencias_bodega",
                sa.Column(
                    "cantidad_reservada",
                    sa.Numeric(18, 4),
                    nullable=False,
                    server_default="0",
                ),
            )

    if "ordenes_pedido" in tablas:

        columnas = {
            col["name"]
            for col in inspector.get_columns(
                "ordenes_pedido",
            )
        }

        if "reserva_aplicada" not in columnas:

            op.add_column(
                "ordenes_pedido",
                sa.Column(
                    "reserva_aplicada",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                ),
            )

        if "bodega_id" not in columnas:

            op.add_column(
                "ordenes_pedido",
                sa.Column(
                    "bodega_id",
                    sa.Integer(),
                    sa.ForeignKey("bodegas.id"),
                ),
            )

    if "pedido_reservas" not in tablas:

        op.create_table(
            "pedido_reservas",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column(
                "pedido_id",
                sa.Integer(),
                sa.ForeignKey("ordenes_pedido.id"),
                nullable=False,
            ),
            sa.Column(
                "bodega_id",
                sa.Integer(),
                sa.ForeignKey("bodegas.id"),
                nullable=False,
            ),
            sa.Column(
                "producto_id",
                sa.Integer(),
                sa.ForeignKey("productos.id"),
                nullable=False,
            ),
            sa.Column(
                "producto_variante_id",
                sa.Integer(),
                sa.ForeignKey("producto_variantes.id"),
            ),
            sa.Column(
                "cantidad",
                sa.Numeric(18, 4),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "activo",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(
                    timezone=True,
                ),
                server_default=sa.func.now(),
            ),
        )

        op.create_index(
            "ix_pedido_reservas_pedido",
            "pedido_reservas",
            ["pedido_id"],
        )


def downgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    tablas = set(
        inspector.get_table_names(),
    )

    if "pedido_reservas" in tablas:

        op.drop_index(
            "ix_pedido_reservas_pedido",
            table_name="pedido_reservas",
        )

        op.drop_table(
            "pedido_reservas",
        )

    if "ordenes_pedido" in tablas:

        columnas = {
            col["name"]
            for col in inspector.get_columns(
                "ordenes_pedido",
            )
        }

        if "bodega_id" in columnas:

            op.drop_column(
                "ordenes_pedido",
                "bodega_id",
            )

        if "reserva_aplicada" in columnas:

            op.drop_column(
                "ordenes_pedido",
                "reserva_aplicada",
            )

    if "existencias_bodega" in tablas:

        columnas = {
            col["name"]
            for col in inspector.get_columns(
                "existencias_bodega",
            )
        }

        if "cantidad_reservada" in columnas:

            op.drop_column(
                "existencias_bodega",
                "cantidad_reservada",
            )
