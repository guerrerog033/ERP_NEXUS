"""Fase 1 — productos: banderas es_kit/maneja_lote/maneja_serie y kit_componentes.

Agrega las tres banderas nuevas a ``productos`` (es_kit,
maneja_lote, maneja_serie) y la tabla ``producto_kit_componentes``
para kits/combos. Las tablas de lote/serie propiamente dichas
(``lotes_series`` / ``existencias_lote_serie``) se agregan en una
migración posterior, una vez definido ese modelo.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0017_producto_kits_flags"
down_revision: Union[str, None] = "0016_producto_unidad_medida_fk"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columnas(tabla: str) -> set[str]:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if tabla not in inspector.get_table_names():

        return set()

    return {
        col["name"]
        for col in inspector.get_columns(tabla)
    }


def _tablas() -> set[str]:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    return set(
        inspector.get_table_names(),
    )


def upgrade() -> None:

    columnas = _columnas("productos")

    for nombre in (
        "es_kit",
        "maneja_lote",
        "maneja_serie",
    ):

        if nombre not in columnas:

            op.add_column(
                "productos",
                sa.Column(
                    nombre,
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                ),
            )

    if "producto_kit_componentes" not in _tablas():

        op.create_table(
            "producto_kit_componentes",
            sa.Column(
                "id",
                sa.Integer(),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column(
                "kit_id",
                sa.Integer(),
                nullable=False,
            ),
            sa.Column(
                "componente_id",
                sa.Integer(),
                nullable=False,
            ),
            sa.Column(
                "cantidad",
                sa.Numeric(18, 4),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["kit_id"],
                ["productos.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["componente_id"],
                ["productos.id"],
                ondelete="RESTRICT",
            ),
            sa.PrimaryKeyConstraint(
                "id",
            ),
            sa.UniqueConstraint(
                "kit_id",
                "componente_id",
                name="uq_kit_componente",
            ),
        )


def downgrade() -> None:

    if "producto_kit_componentes" in _tablas():

        op.drop_table(
            "producto_kit_componentes",
        )

    columnas = _columnas("productos")

    for nombre in (
        "es_kit",
        "maneja_lote",
        "maneja_serie",
    ):

        if nombre in columnas:

            op.drop_column(
                "productos",
                nombre,
            )
