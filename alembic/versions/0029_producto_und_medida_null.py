"""Corrige el NOT NULL huérfano en productos.unidad_medida (legacy).

La migración 0016 introdujo unidad_medida_id (FK al catálogo real de
unidades) y dejó "intacta" la columna de texto libre unidad_medida
como respaldo histórico — pero esa columna venía con
NOT NULL DEFAULT 'Und' desde la creación original de la tabla y
0016 nunca la relajó. El modelo SQLAlchemy sí quedó marcado
nullable=True al renombrar el atributo a unidad_medida_legacy, y
ningún código del sistema la vuelve a escribir desde entonces: el
INSERT generado por el ORM manda NULL explícito para esa columna
(el DEFAULT de Postgres solo aplica cuando la columna se omite del
INSERT, no cuando se manda NULL), así que cualquier alta de producto
por fuera de los datos ya existentes viola la restricción.

Alinea la base real con lo que el modelo ya declaraba.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0029_producto_und_medida_null"
down_revision: Union[str, None] = "0028_merge_heads"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.alter_column(
        "productos",
        "unidad_medida",
        existing_type=sa.String(length=20),
        nullable=True,
        existing_server_default=sa.text("'Und'::character varying"),
    )


def downgrade() -> None:

    op.execute(
        "UPDATE productos SET unidad_medida = 'Und' "
        "WHERE unidad_medida IS NULL",
    )

    op.alter_column(
        "productos",
        "unidad_medida",
        existing_type=sa.String(length=20),
        nullable=False,
        existing_server_default=sa.text("'Und'::character varying"),
    )
