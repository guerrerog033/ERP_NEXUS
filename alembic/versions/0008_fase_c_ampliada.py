"""Revisiones Alembic — Fase C ampliada: OC ↔ factura."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_fase_c_ampliada"
down_revision: Union[str, None] = "0007_fase_b_existencias_bodega"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columna_existe(
    inspector,
    tabla: str,
    columna: str,
) -> bool:

    return columna in {
        col["name"]
        for col in inspector.get_columns(
            tabla,
        )
    }


def upgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    tablas = set(
        inspector.get_table_names(),
    )

    if "facturas_compra" in tablas:

        if not _columna_existe(
            inspector,
            "facturas_compra",
            "orden_compra_id",
        ):

            op.add_column(
                "facturas_compra",
                sa.Column(
                    "orden_compra_id",
                    sa.Integer(),
                    sa.ForeignKey(
                        "ordenes_compra.id",
                    ),
                    nullable=True,
                ),
            )

        if not _columna_existe(
            inspector,
            "facturas_compra",
            "inventario_aplicado",
        ):

            op.add_column(
                "facturas_compra",
                sa.Column(
                    "inventario_aplicado",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                ),
            )

        if not _columna_existe(
            inspector,
            "facturas_compra",
            "match_estado",
        ):

            op.add_column(
                "facturas_compra",
                sa.Column(
                    "match_estado",
                    sa.String(30),
                    nullable=True,
                ),
            )

        if not _columna_existe(
            inspector,
            "facturas_compra",
            "match_mensaje",
        ):

            op.add_column(
                "facturas_compra",
                sa.Column(
                    "match_mensaje",
                    sa.String(500),
                    nullable=True,
                ),
            )

    if "factura_compra_detalles" in tablas:

        if not _columna_existe(
            inspector,
            "factura_compra_detalles",
            "orden_detalle_id",
        ):

            op.add_column(
                "factura_compra_detalles",
                sa.Column(
                    "orden_detalle_id",
                    sa.Integer(),
                    sa.ForeignKey(
                        "orden_compra_detalles.id",
                    ),
                    nullable=True,
                ),
            )


def downgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    tablas = set(
        inspector.get_table_names(),
    )

    if "factura_compra_detalles" in tablas:

        if _columna_existe(
            inspector,
            "factura_compra_detalles",
            "orden_detalle_id",
        ):

            op.drop_column(
                "factura_compra_detalles",
                "orden_detalle_id",
            )

    if "facturas_compra" in tablas:

        for columna in (
            "match_mensaje",
            "match_estado",
            "inventario_aplicado",
            "orden_compra_id",
        ):

            if _columna_existe(
                inspector,
                "facturas_compra",
                columna,
            ):

                op.drop_column(
                    "facturas_compra",
                    columna,
                )
