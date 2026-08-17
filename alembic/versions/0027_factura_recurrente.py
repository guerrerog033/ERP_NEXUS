"""Ventas: facturación recurrente.

Agrega las tablas facturas_recurrentes / factura_recurrente_detalles:
plantillas que generan una FacturaVenta real cada vez que se cumple
su periodicidad (mensual, quincenal, trimestral, anual).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0027_factura_recurrente"
down_revision: Union[str, None] = "0026_orden_compra_aprobacion"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tablas() -> set[str]:

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    return set(inspector.get_table_names())


def upgrade() -> None:

    tablas = _tablas()

    if "facturas_recurrentes" not in tablas:

        op.create_table(
            "facturas_recurrentes",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column(
                "nombre",
                sa.String(150),
                nullable=False,
            ),
            sa.Column(
                "cliente_id",
                sa.Integer(),
                sa.ForeignKey("terceros.id"),
                nullable=False,
            ),
            sa.Column(
                "periodicidad",
                sa.String(20),
                nullable=False,
                server_default="mensual",
            ),
            sa.Column(
                "proxima_fecha",
                sa.Date(),
                nullable=False,
            ),
            sa.Column(
                "ultima_generada_en",
                sa.Date(),
                nullable=True,
            ),
            sa.Column(
                "facturas_generadas",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "observaciones",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "activa",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
            ),
        )

    if "factura_recurrente_detalles" not in tablas:

        op.create_table(
            "factura_recurrente_detalles",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column(
                "plantilla_id",
                sa.Integer(),
                sa.ForeignKey(
                    "facturas_recurrentes.id",
                    ondelete="CASCADE",
                ),
                nullable=False,
            ),
            sa.Column(
                "producto_id",
                sa.Integer(),
                sa.ForeignKey("productos.id"),
                nullable=True,
            ),
            sa.Column(
                "descripcion",
                sa.String(250),
                nullable=False,
            ),
            sa.Column(
                "cantidad",
                sa.Numeric(18, 4),
                nullable=False,
                server_default="1",
            ),
            sa.Column(
                "precio_unitario",
                sa.Numeric(18, 2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "impuesto_id",
                sa.Integer(),
                sa.ForeignKey("impuestos.id"),
                nullable=True,
            ),
            sa.Column(
                "precio_incluye_iva",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "orden",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )


def downgrade() -> None:

    tablas = _tablas()

    if "factura_recurrente_detalles" in tablas:

        op.drop_table("factura_recurrente_detalles")

    if "facturas_recurrentes" in tablas:

        op.drop_table("facturas_recurrentes")
