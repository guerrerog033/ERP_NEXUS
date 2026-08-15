"""Revisiones Alembic — Fase 6: Numeric logística/POS y pos_ventas_log."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_numeric_fase6"
down_revision: Union[str, None] = "0004_numeric_fase5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _alterar_si_existe(
    tabla: str,
    columna: str,
    tipo: sa.types.TypeEngine,
    *,
    using: str,
) -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    if tabla not in inspector.get_table_names():

        return

    columnas = {
        col["name"]
        for col in inspector.get_columns(
            tabla,
        )
    }

    if columna not in columnas:

        return

    op.alter_column(
        tabla,
        columna,
        type_=tipo,
        postgresql_using=using,
    )


def upgrade() -> None:

    for columna in (
        "latitud",
        "longitud",
    ):

        _alterar_si_existe(
            "despachos_pedido",
            columna,
            sa.Numeric(
                10,
                7,
            ),
            using=(
                f"{columna}::numeric(10,7)"
            ),
        )

    _alterar_si_existe(
        "despachos_pedido",
        "costo_flete",
        sa.Numeric(
            18,
            2,
        ),
        using="costo_flete::numeric(18,2)",
    )

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    if (
        "pos_ventas_log"
        not in inspector.get_table_names()
    ):

        op.create_table(
            "pos_ventas_log",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column(
                "factura_id",
                sa.Integer(),
                sa.ForeignKey(
                    "facturas_venta.id",
                ),
                nullable=False,
            ),
            sa.Column(
                "total",
                sa.Numeric(
                    18,
                    2,
                ),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "recibido",
                sa.Numeric(
                    18,
                    2,
                ),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "cambio",
                sa.Numeric(
                    18,
                    2,
                ),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "metodo_pago",
                sa.String(
                    30,
                ),
                nullable=False,
                server_default="efectivo",
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
                "fecha_creacion",
                sa.DateTime(
                    timezone=True,
                ),
                server_default=sa.text(
                    "now()",
                ),
            ),
        )


def downgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    if (
        "pos_ventas_log"
        in inspector.get_table_names()
    ):

        op.drop_table(
            "pos_ventas_log",
        )

    for columna in (
        "latitud",
        "longitud",
        "costo_flete",
    ):

        _alterar_si_existe(
            "despachos_pedido",
            columna,
            sa.Float(),
            using=(
                f"{columna}::double precision"
            ),
        )
