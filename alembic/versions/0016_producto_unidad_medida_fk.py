"""Fase 1 — productos: unidad de medida como catálogo (FK), no texto libre.

La columna ``productos.unidad_medida`` (texto libre, antes limitada
a 7 valores hardcodeados en código) queda intacta como respaldo
histórico. Se agrega ``productos.unidad_medida_id`` apuntando al
catálogo real (``unidades_medida``, ya existente desde la Fase 21 —
0013), y se hace un backfill de los datos existentes: cada valor de
texto ya usado se mapea (o se crea, si no coincide con ninguno de
los predeterminados) a una fila del catálogo.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0016_producto_unidad_medida_fk"
down_revision: Union[str, None] = "0015_tercero_cuentas_bancarias"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UNIDADES_PREDETERMINADAS = (
    ("Und", "Unidad", "94"),
    ("Par", "Par", "PR"),
    ("Caja", "Caja", "XBX"),
    ("Pq", "Paquete", "PK"),
    ("Mts", "Metro", "MTR"),
    ("Gls", "Galón", "GLL"),
    ("Lts", "Litro", "LTR"),
)


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

    columnas = _columnas("productos")

    if "unidad_medida_id" not in columnas:

        op.add_column(
            "productos",
            sa.Column(
                "unidad_medida_id",
                sa.Integer(),
                nullable=True,
            ),
        )

        op.create_foreign_key(
            "fk_productos_unidad_medida_id",
            "productos",
            "unidades_medida",
            ["unidad_medida_id"],
            ["id"],
            ondelete="SET NULL",
        )

    bind = op.get_bind()

    for codigo, nombre, codigo_dian in UNIDADES_PREDETERMINADAS:

        existe = bind.execute(
            sa.text(
                "SELECT 1 FROM unidades_medida WHERE codigo = :codigo",
            ),
            {"codigo": codigo},
        ).first()

        if existe is None:

            bind.execute(
                sa.text(
                    "INSERT INTO unidades_medida "
                    "(codigo, nombre, codigo_dian, activo) "
                    "VALUES (:codigo, :nombre, :codigo_dian, true)",
                ),
                {
                    "codigo": codigo,
                    "nombre": nombre,
                    "codigo_dian": codigo_dian,
                },
            )

    valores_sin_mapear = bind.execute(
        sa.text(
            "SELECT DISTINCT unidad_medida FROM productos "
            "WHERE unidad_medida IS NOT NULL "
            "AND unidad_medida NOT IN ("
            "SELECT codigo FROM unidades_medida"
            ")",
        ),
    ).fetchall()

    for (valor,) in valores_sin_mapear:

        valor_limpio = (valor or "").strip()

        if not valor_limpio:

            continue

        bind.execute(
            sa.text(
                "INSERT INTO unidades_medida (codigo, nombre, activo) "
                "VALUES (:codigo, :nombre, true)",
            ),
            {
                "codigo": valor_limpio,
                "nombre": valor_limpio,
            },
        )

    bind.execute(
        sa.text(
            "UPDATE productos SET unidad_medida_id = ("
            "SELECT id FROM unidades_medida "
            "WHERE unidades_medida.codigo = productos.unidad_medida"
            ") WHERE unidad_medida_id IS NULL "
            "AND unidad_medida IS NOT NULL",
        ),
    )


def downgrade() -> None:

    columnas = _columnas("productos")

    if "unidad_medida_id" in columnas:

        op.drop_constraint(
            "fk_productos_unidad_medida_id",
            "productos",
            type_="foreignkey",
        )

        op.drop_column(
            "productos",
            "unidad_medida_id",
        )
