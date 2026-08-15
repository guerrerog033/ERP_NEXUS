"""Revisiones Alembic — Fase C complementos."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009_fase_c_complementos"
down_revision: Union[str, None] = "0008_fase_c_ampliada"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    tablas = set(
        inspector.get_table_names(),
    )

    if (
        "factura_compra_eventos_radian"
        not in tablas
    ):

        op.create_table(
            "factura_compra_eventos_radian",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column(
                "factura_id",
                sa.Integer(),
                sa.ForeignKey(
                    "facturas_compra.id",
                ),
                nullable=False,
            ),
            sa.Column(
                "codigo_evento",
                sa.String(10),
                nullable=False,
            ),
            sa.Column(
                "cude",
                sa.String(100),
            ),
            sa.Column(
                "estado",
                sa.String(30),
                nullable=False,
                server_default="enviado",
            ),
            sa.Column(
                "mensaje",
                sa.String(500),
            ),
            sa.Column(
                "ruta_xml",
                sa.String(500),
            ),
            sa.Column(
                "forzado",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "fecha_evento",
                sa.DateTime(
                    timezone=True,
                ),
                server_default=sa.func.now(),
            ),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(
                    timezone=True,
                ),
                server_default=sa.func.now(),
            ),
        )

        op.create_index(
            "ix_fc_evento_radian_factura",
            "factura_compra_eventos_radian",
            ["factura_id"],
        )

    if (
        "notas_credito_compra"
        not in tablas
    ):

        op.create_table(
            "notas_credito_compra",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column(
                "numero",
                sa.String(30),
                unique=True,
                nullable=False,
            ),
            sa.Column(
                "fecha",
                sa.Date(),
                nullable=False,
            ),
            sa.Column(
                "proveedor_id",
                sa.Integer(),
                sa.ForeignKey("terceros.id"),
                nullable=False,
            ),
            sa.Column(
                "factura_compra_id",
                sa.Integer(),
                sa.ForeignKey("facturas_compra.id"),
                nullable=False,
            ),
            sa.Column(
                "motivo",
                sa.String(250),
            ),
            sa.Column(
                "factura_cufe",
                sa.String(100),
            ),
            sa.Column(
                "cufe",
                sa.String(100),
            ),
            sa.Column(
                "subtotal",
                sa.Numeric(18, 2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "iva",
                sa.Numeric(18, 2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "total",
                sa.Numeric(18, 2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "estado",
                sa.String(20),
                nullable=False,
                server_default="borrador",
            ),
            sa.Column(
                "contabilizado",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "inventario_aplicado",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "asiento_id",
                sa.Integer(),
                sa.ForeignKey("asientos_contables.id"),
            ),
            sa.Column(
                "observaciones",
                sa.Text(),
            ),
            sa.Column(
                "activo",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(
                    timezone=True,
                ),
                server_default=sa.func.now(),
            ),
        )

        op.create_table(
            "nota_credito_compra_detalles",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column(
                "nota_credito_id",
                sa.Integer(),
                sa.ForeignKey(
                    "notas_credito_compra.id",
                ),
                nullable=False,
            ),
            sa.Column(
                "producto_id",
                sa.Integer(),
                sa.ForeignKey("productos.id"),
            ),
            sa.Column(
                "producto_variante_id",
                sa.Integer(),
                sa.ForeignKey(
                    "producto_variantes.id",
                ),
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
            ),
            sa.Column(
                "precio_incluye_iva",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "total_linea",
                sa.Numeric(18, 2),
                nullable=False,
                server_default="0",
            ),
            sa.Column(
                "orden",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )


def downgrade() -> None:

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    tablas = set(
        inspector.get_table_names(),
    )

    if (
        "nota_credito_compra_detalles"
        in tablas
    ):

        op.drop_table(
            "nota_credito_compra_detalles",
        )

    if "notas_credito_compra" in tablas:

        op.drop_table(
            "notas_credito_compra",
        )

    if (
        "factura_compra_eventos_radian"
        in tablas
    ):

        op.drop_index(
            "ix_fc_evento_radian_factura",
            table_name="factura_compra_eventos_radian",
        )

        op.drop_table(
            "factura_compra_eventos_radian",
        )
