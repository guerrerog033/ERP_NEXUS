"""Facturas de venta: moneda de referencia (multi-moneda informativa).

Agrega moneda_referencia/tasa_cambio_referencia a facturas_venta.
Los totales de la factura (subtotal/iva/total) siguen siempre en
COP — son los que se envían a la DIAN y los que usa contabilidad.
La moneda de referencia es solo informativa: se muestra en el
documento impreso como equivalencia para el cliente que factura en
otra divisa (ej. servicios de exportación en USD).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0027b_factura_venta_moneda_ref"
down_revision: Union[str, None] = "0026_orden_compra_aprobacion"
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

    existentes = _columnas("facturas_venta")

    if "moneda_referencia" not in existentes:

        op.add_column(
            "facturas_venta",
            sa.Column(
                "moneda_referencia",
                sa.String(3),
                nullable=True,
            ),
        )

    if "tasa_cambio_referencia" not in existentes:

        op.add_column(
            "facturas_venta",
            sa.Column(
                "tasa_cambio_referencia",
                sa.Numeric(18, 6),
                nullable=True,
            ),
        )


def downgrade() -> None:

    existentes = _columnas("facturas_venta")

    if "tasa_cambio_referencia" in existentes:

        op.drop_column(
            "facturas_venta",
            "tasa_cambio_referencia",
        )

    if "moneda_referencia" in existentes:

        op.drop_column(
            "facturas_venta",
            "moneda_referencia",
        )
