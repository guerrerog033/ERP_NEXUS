"""Fase 5 — terceros: token de acceso al portal de autoconsulta.

Agrega la columna ``portal_token`` a ``terceros`` para el portal
web de clientes/proveedores (ver facturas y estado de cartera sin
necesidad de una cuenta de usuario del ERP).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0023_tercero_portal_token"
down_revision: Union[str, None] = "0022_ce_formato_impresion"
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


def _indices(tabla: str) -> set[str]:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if tabla not in inspector.get_table_names():

        return set()

    return {
        indice["name"]
        for indice in inspector.get_indexes(tabla)
    }


def upgrade() -> None:

    if "portal_token" not in _columnas(
        "terceros",
    ):

        op.add_column(
            "terceros",
            sa.Column(
                "portal_token",
                sa.String(64),
                nullable=True,
            ),
        )

    if "ix_terceros_portal_token" not in _indices(
        "terceros",
    ):

        op.create_index(
            "ix_terceros_portal_token",
            "terceros",
            ["portal_token"],
            unique=True,
        )


def downgrade() -> None:

    if "ix_terceros_portal_token" in _indices(
        "terceros",
    ):

        op.drop_index(
            "ix_terceros_portal_token",
            table_name="terceros",
        )

    if "portal_token" in _columnas(
        "terceros",
    ):

        op.drop_column(
            "terceros",
            "portal_token",
        )
