"""Merge de cabezas: facturación recurrente + moneda de referencia.

Las migraciones 0027 (facturación recurrente) y 0027b (moneda de
referencia en facturas de venta) se desarrollaron en paralelo sobre
la misma base (0026) porque sus respectivos PR estaban abiertos al
mismo tiempo. Tocan tablas distintas, sin conflicto de datos — esta
migración solo unifica el árbol de Alembic en una sola cabeza.
"""

from typing import Sequence, Union

revision: str = "0028_merge_heads"
down_revision: Union[str, Sequence[str], None] = (
    "0027_factura_recurrente",
    "0027b_factura_venta_moneda_ref",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    pass


def downgrade() -> None:

    pass
