"""Productos: escalones de precio por volumen.

Agrega la tabla ``producto_precios_volumen`` para definir precios
que se aplican automáticamente a partir de cierta cantidad en una
línea de documento (independiente de las listas de precio).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0025_producto_precio_volumen"
down_revision: Union[str, None] = "0024_exento_bloqueo_cartera"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tablas() -> set[str]:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    return set(inspector.get_table_names())


def upgrade() -> None:

    if "producto_precios_volumen" in _tablas():

        return

    op.create_table(
        "producto_precios_volumen",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "producto_id",
            sa.Integer(),
            sa.ForeignKey(
                "productos.id",
                ondelete="CASCADE",
            ),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "cantidad_minima",
            sa.Numeric(18, 4),
            nullable=False,
        ),
        sa.Column(
            "precio",
            sa.Numeric(18, 2),
            nullable=False,
            server_default="0",
        ),
        sa.UniqueConstraint(
            "producto_id",
            "cantidad_minima",
            name="uq_producto_precio_volumen",
        ),
    )


def downgrade() -> None:

    if "producto_precios_volumen" in _tablas():

        op.drop_table("producto_precios_volumen")
