"""Terceros: exención al bloqueo automático por cartera vencida.

Agrega ``terceros.exento_bloqueo_cartera`` para poder excluir
clientes puntuales del bloqueo de nuevas facturas de venta cuando
tienen cartera vencida (configurable en Cartera > Configuración).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0024_exento_bloqueo_cartera"
down_revision: Union[str, None] = "0023_tercero_portal_token"
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

    if "exento_bloqueo_cartera" not in _columnas(
        "terceros",
    ):

        op.add_column(
            "terceros",
            sa.Column(
                "exento_bloqueo_cartera",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )


def downgrade() -> None:

    if "exento_bloqueo_cartera" in _columnas(
        "terceros",
    ):

        op.drop_column(
            "terceros",
            "exento_bloqueo_cartera",
        )
