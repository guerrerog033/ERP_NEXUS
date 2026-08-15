"""Fase 1 — inventario: control por lote y número de serie.

Agrega las tablas lotes_series y existencias_lote_serie, más
movimientos_inventario.lote_serie_id (nullable — la mayoría de
movimientos no involucran un producto controlado por lote/serie).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0018_lote_serie"
down_revision: Union[str, None] = "0017_producto_kits_flags"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tablas() -> set[str]:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    return set(
        inspector.get_table_names(),
    )


def _columnas(tabla: str) -> set[str]:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if tabla not in inspector.get_table_names():

        return set()

    return {
        col["name"]
        for col in inspector.get_columns(tabla)
    }


def upgrade() -> None:

    tablas = _tablas()

    if "lotes_series" not in tablas:

        op.create_table(
            "lotes_series",
            sa.Column(
                "id",
                sa.Integer(),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column(
                "producto_id",
                sa.Integer(),
                nullable=False,
            ),
            sa.Column(
                "tipo",
                sa.String(length=10),
                nullable=False,
            ),
            sa.Column(
                "numero",
                sa.String(length=60),
                nullable=False,
            ),
            sa.Column(
                "fecha_fabricacion",
                sa.Date(),
                nullable=True,
            ),
            sa.Column(
                "fecha_vencimiento",
                sa.Date(),
                nullable=True,
            ),
            sa.Column(
                "notas",
                sa.String(length=300),
                nullable=True,
            ),
            sa.Column(
                "activo",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(
                ["producto_id"],
                ["productos.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint(
                "id",
            ),
            sa.UniqueConstraint(
                "producto_id",
                "numero",
                name="uq_producto_lote_serie_numero",
            ),
        )

    tablas = _tablas()

    if "existencias_lote_serie" not in tablas:

        op.create_table(
            "existencias_lote_serie",
            sa.Column(
                "id",
                sa.Integer(),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column(
                "bodega_id",
                sa.Integer(),
                nullable=False,
            ),
            sa.Column(
                "lote_serie_id",
                sa.Integer(),
                nullable=False,
            ),
            sa.Column(
                "cantidad",
                sa.Numeric(18, 4),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["bodega_id"],
                ["bodegas.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["lote_serie_id"],
                ["lotes_series.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint(
                "id",
            ),
            sa.UniqueConstraint(
                "bodega_id",
                "lote_serie_id",
                name="uq_bodega_lote_serie",
            ),
        )

    columnas_movimientos = _columnas(
        "movimientos_inventario",
    )

    if "lote_serie_id" not in columnas_movimientos:

        op.add_column(
            "movimientos_inventario",
            sa.Column(
                "lote_serie_id",
                sa.Integer(),
                nullable=True,
            ),
        )

        op.create_foreign_key(
            "fk_movimientos_lote_serie_id",
            "movimientos_inventario",
            "lotes_series",
            ["lote_serie_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:

    columnas_movimientos = _columnas(
        "movimientos_inventario",
    )

    if "lote_serie_id" in columnas_movimientos:

        op.drop_constraint(
            "fk_movimientos_lote_serie_id",
            "movimientos_inventario",
            type_="foreignkey",
        )

        op.drop_column(
            "movimientos_inventario",
            "lote_serie_id",
        )

    tablas = _tablas()

    if "existencias_lote_serie" in tablas:

        op.drop_table(
            "existencias_lote_serie",
        )

    if "lotes_series" in tablas:

        op.drop_table(
            "lotes_series",
        )
