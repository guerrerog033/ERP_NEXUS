"""Fase 2 — órdenes de compra: columna formato_impresion.

Agrega la columna ``formato_impresion`` a ``ordenes_compra`` para
poder elegir entre los formatos visuales (carta/corporativo/
moderno/compacto/tirilla/estandar) al imprimir, igual que en
cotizaciones.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0019_oc_formato_impresion"
down_revision: Union[str, None] = "0018_lote_serie"
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
        "ordenes_compra",
    ):

        op.add_column(
            "ordenes_compra",
            sa.Column(
                "formato_impresion",
                sa.String(20),
                nullable=False,
                server_default="carta",
            ),
        )


def downgrade() -> None:

    if "formato_impresion" in _columnas(
        "ordenes_compra",
    ):

        op.drop_column(
            "ordenes_compra",
            "formato_impresion",
        )
