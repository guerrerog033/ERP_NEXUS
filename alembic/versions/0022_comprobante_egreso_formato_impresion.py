"""Fase 2 — comprobantes de egreso: columna formato_impresion.

Agrega la columna ``formato_impresion`` a ``comprobantes_egreso``,
igual que en recibos de caja y órdenes/facturas de compra.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0022_ce_formato_impresion"
down_revision: Union[str, None] = "0021_rc_formato_impresion"
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


def upgrade() -> None:

    if "formato_impresion" not in _columnas(
        "comprobantes_egreso",
    ):

        op.add_column(
            "comprobantes_egreso",
            sa.Column(
                "formato_impresion",
                sa.String(20),
                nullable=False,
                server_default="carta",
            ),
        )


def downgrade() -> None:

    if "formato_impresion" in _columnas(
        "comprobantes_egreso",
    ):

        op.drop_column(
            "comprobantes_egreso",
            "formato_impresion",
        )
