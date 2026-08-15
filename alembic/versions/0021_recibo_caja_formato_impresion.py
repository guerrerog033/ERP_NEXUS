"""Fase 2 — recibos de caja: columna formato_impresion.

Agrega la columna ``formato_impresion`` a ``recibos_caja``, igual
que en órdenes/facturas de compra y cotizaciones.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0021_rc_formato_impresion"
down_revision: Union[str, None] = "0020_fc_formato_impresion"
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
        "recibos_caja",
    ):

        op.add_column(
            "recibos_caja",
            sa.Column(
                "formato_impresion",
                sa.String(20),
                nullable=False,
                server_default="carta",
            ),
        )


def downgrade() -> None:

    if "formato_impresion" in _columnas(
        "recibos_caja",
    ):

        op.drop_column(
            "recibos_caja",
            "formato_impresion",
        )
