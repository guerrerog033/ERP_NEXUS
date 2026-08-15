"""Fase 22 — productos e inventario: tipos, índices y JSONB."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0014_producto_inventario"
down_revision: Union[str, None] = "0013_fase21_consolidacion"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NUMERIC_18_2 = sa.Numeric(18, 2)
NUMERIC_18_4 = sa.Numeric(18, 4)


def _columnas(tabla: str) -> set[str]:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if tabla not in inspector.get_table_names():

        return set()

    return {
        col["name"]
        for col in inspector.get_columns(tabla)
    }


def _indices(tabla: str) -> set[str]:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    return {
        idx["name"]
        for idx in inspector.get_indexes(tabla)
    }


def upgrade() -> None:

    bind = op.get_bind()

    if bind.dialect.name != "postgresql":

        return

    # --- productos ---

    if "productos" in sa.inspect(bind).get_table_names():

        op.alter_column(
            "productos",
            "descripcion",
            existing_type=sa.String(500),
            type_=sa.Text(),
            existing_nullable=True,
        )

        op.alter_column(
            "productos",
            "unidad_medida",
            existing_type=sa.String(length=10),
            type_=sa.String(length=20),
            existing_nullable=False,
        )

        for columna in (
            "precio_venta",
            "costo",
        ):

            op.alter_column(
                "productos",
                columna,
                existing_type=sa.Float(),
                type_=NUMERIC_18_2,
                postgresql_using=f"{columna}::numeric(18,2)",
                existing_nullable=False,
            )

        for columna in (
            "existencia",
            "stock_minimo",
        ):

            op.alter_column(
                "productos",
                columna,
                existing_type=sa.Float(),
                type_=NUMERIC_18_4,
                postgresql_using=f"{columna}::numeric(18,4)",
                existing_nullable=False,
            )

        op.alter_column(
            "productos",
            "atributos_variante",
            existing_type=postgresql.JSON(astext_type=sa.Text()),
            type_=postgresql.JSONB(astext_type=sa.Text()),
            postgresql_using="atributos_variante::jsonb",
            existing_nullable=True,
        )

        indices = _indices("productos")

        if "ix_productos_codigo" not in indices:

            op.create_index(
                "ix_productos_codigo",
                "productos",
                ["codigo"],
                unique=False,
            )

        if "ix_productos_codigo_barras" not in indices:

            op.create_index(
                "ix_productos_codigo_barras",
                "productos",
                ["codigo_barras"],
                unique=False,
            )

    # --- producto_variantes ---

    if "producto_variantes" in sa.inspect(bind).get_table_names():

        op.alter_column(
            "producto_variantes",
            "codigo",
            existing_type=sa.String(length=40),
            type_=sa.String(length=50),
            existing_nullable=False,
        )

        for columna in (
            "talla",
            "color",
            "calibre",
            "largo",
        ):

            op.alter_column(
                "producto_variantes",
                columna,
                existing_type=sa.String(length=30),
                type_=sa.String(length=50),
                existing_nullable=True,
            )

        for columna in (
            "precio_venta",
            "costo",
        ):

            op.alter_column(
                "producto_variantes",
                columna,
                existing_type=sa.Float(),
                type_=NUMERIC_18_2,
                postgresql_using=f"{columna}::numeric(18,2)",
                existing_nullable=True,
            )

        op.alter_column(
            "producto_variantes",
            "existencia",
            existing_type=sa.Float(),
            type_=NUMERIC_18_4,
            postgresql_using="existencia::numeric(18,4)",
            existing_nullable=False,
        )

        op.alter_column(
            "producto_variantes",
            "atributos",
            existing_type=postgresql.JSON(astext_type=sa.Text()),
            type_=postgresql.JSONB(astext_type=sa.Text()),
            postgresql_using="atributos::jsonb",
            existing_nullable=True,
        )

        indices = _indices("producto_variantes")

        if "ix_producto_variantes_producto_id" not in indices:

            op.create_index(
                "ix_producto_variantes_producto_id",
                "producto_variantes",
                ["producto_id"],
                unique=False,
            )

    # --- producto_precios ---

    if "producto_precios" in sa.inspect(bind).get_table_names():

        op.alter_column(
            "producto_precios",
            "precio",
            existing_type=sa.Float(),
            type_=NUMERIC_18_2,
            postgresql_using="precio::numeric(18,2)",
            existing_nullable=False,
        )

        indices = _indices("producto_precios")

        if "ix_producto_precios_producto_id" not in indices:

            op.create_index(
                "ix_producto_precios_producto_id",
                "producto_precios",
                ["producto_id"],
                unique=False,
            )

    # --- bodegas ---

    if "bodegas" in sa.inspect(bind).get_table_names():

        op.alter_column(
            "bodegas",
            "codigo",
            existing_type=sa.String(length=20),
            type_=sa.String(length=30),
            existing_nullable=False,
        )

        op.alter_column(
            "bodegas",
            "nombre",
            existing_type=sa.String(length=120),
            type_=sa.String(length=150),
            existing_nullable=False,
        )

        op.alter_column(
            "bodegas",
            "responsable",
            existing_type=sa.String(length=120),
            type_=sa.String(length=150),
            existing_nullable=True,
        )

    # --- movimientos_inventario ---

    if "movimientos_inventario" in sa.inspect(bind).get_table_names():

        op.alter_column(
            "movimientos_inventario",
            "tipo",
            existing_type=sa.String(length=20),
            type_=sa.String(length=30),
            existing_nullable=False,
        )

        op.alter_column(
            "movimientos_inventario",
            "referencia",
            existing_type=sa.String(length=40),
            type_=sa.String(length=50),
            existing_nullable=True,
        )

        op.alter_column(
            "movimientos_inventario",
            "observaciones",
            existing_type=sa.String(length=250),
            type_=sa.Text(),
            existing_nullable=True,
        )

        indices = _indices("movimientos_inventario")

        if "ix_movimientos_inventario_bodega_id" not in indices:

            op.create_index(
                "ix_movimientos_inventario_bodega_id",
                "movimientos_inventario",
                ["bodega_id"],
                unique=False,
            )

        if "ix_movimientos_inventario_producto_id" not in indices:

            op.create_index(
                "ix_movimientos_inventario_producto_id",
                "movimientos_inventario",
                ["producto_id"],
                unique=False,
            )

    # --- existencias_bodega ---

    if "existencias_bodega" in sa.inspect(bind).get_table_names():

        indices = _indices("existencias_bodega")

        if "ix_existencias_bodega_bodega_id" not in indices:

            op.create_index(
                "ix_existencias_bodega_bodega_id",
                "existencias_bodega",
                ["bodega_id"],
                unique=False,
            )

        if "ix_existencias_bodega_producto_id" not in indices:

            op.create_index(
                "ix_existencias_bodega_producto_id",
                "existencias_bodega",
                ["producto_id"],
                unique=False,
            )


def downgrade() -> None:

    bind = op.get_bind()

    if bind.dialect.name != "postgresql":

        return

    for nombre in (
        "ix_existencias_bodega_producto_id",
        "ix_existencias_bodega_bodega_id",
        "ix_movimientos_inventario_producto_id",
        "ix_movimientos_inventario_bodega_id",
        "ix_producto_precios_producto_id",
        "ix_producto_variantes_producto_id",
        "ix_productos_codigo_barras",
        "ix_productos_codigo",
    ):

        op.execute(
            sa.text(
                f"DROP INDEX IF EXISTS {nombre}",
            ),
        )
