"""Órdenes de compra: aprobación multinivel por monto.

Agrega el flujo de aprobación (uno o dos niveles, según montos
configurables) que se debe superar antes de poder registrar
recepciones contra una orden de compra.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0026_orden_compra_aprobacion"
down_revision: Union[str, None] = "0025_producto_precio_volumen"
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

    existentes = _columnas("ordenes_compra")

    if "estado_aprobacion" not in existentes:

        op.add_column(
            "ordenes_compra",
            sa.Column(
                "estado_aprobacion",
                sa.String(20),
                nullable=False,
                server_default="no_aplica",
            ),
        )

    if "aprobado_nivel1_por" not in existentes:

        op.add_column(
            "ordenes_compra",
            sa.Column(
                "aprobado_nivel1_por",
                sa.String(120),
                nullable=True,
            ),
        )

    if "aprobado_nivel1_en" not in existentes:

        op.add_column(
            "ordenes_compra",
            sa.Column(
                "aprobado_nivel1_en",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    if "aprobado_nivel2_por" not in existentes:

        op.add_column(
            "ordenes_compra",
            sa.Column(
                "aprobado_nivel2_por",
                sa.String(120),
                nullable=True,
            ),
        )

    if "aprobado_nivel2_en" not in existentes:

        op.add_column(
            "ordenes_compra",
            sa.Column(
                "aprobado_nivel2_en",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    if "motivo_rechazo" not in existentes:

        op.add_column(
            "ordenes_compra",
            sa.Column(
                "motivo_rechazo",
                sa.String(300),
                nullable=True,
            ),
        )


def downgrade() -> None:

    existentes = _columnas("ordenes_compra")

    for columna in (
        "motivo_rechazo",
        "aprobado_nivel2_en",
        "aprobado_nivel2_por",
        "aprobado_nivel1_en",
        "aprobado_nivel1_por",
        "estado_aprobacion",
    ):

        if columna in existentes:

            op.drop_column(
                "ordenes_compra",
                columna,
            )
