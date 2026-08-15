"""Revisiones Alembic — guías remisión electrónica."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0010_guias_remision_electronica"
down_revision: Union[str, None] = "0009_fase_c_complementos"
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
        "guias_remision_electronica"
        not in tablas
    ):

        op.create_table(
            "guias_remision_electronica",
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
                "prefijo",
                sa.String(10),
            ),
            sa.Column(
                "consecutivo_dian",
                sa.String(20),
            ),
            sa.Column(
                "fecha",
                sa.Date(),
                nullable=False,
            ),
            sa.Column(
                "remision_id",
                sa.Integer(),
                sa.ForeignKey("remisiones_venta.id"),
            ),
            sa.Column(
                "remision_numero",
                sa.String(30),
            ),
            sa.Column(
                "cliente_id",
                sa.Integer(),
                sa.ForeignKey("terceros.id"),
                nullable=False,
            ),
            sa.Column(
                "subtotal",
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
                "direccion_origen",
                sa.String(250),
            ),
            sa.Column(
                "ciudad_origen",
                sa.String(80),
            ),
            sa.Column(
                "departamento_origen",
                sa.String(80),
            ),
            sa.Column(
                "direccion_destino",
                sa.String(250),
            ),
            sa.Column(
                "ciudad_destino",
                sa.String(80),
            ),
            sa.Column(
                "departamento_destino",
                sa.String(80),
            ),
            sa.Column(
                "conductor",
                sa.String(120),
            ),
            sa.Column(
                "vehiculo",
                sa.String(80),
            ),
            sa.Column(
                "placa",
                sa.String(20),
            ),
            sa.Column(
                "transportadora",
                sa.String(120),
            ),
            sa.Column(
                "cude",
                sa.String(100),
                unique=True,
            ),
            sa.Column(
                "estado",
                sa.String(20),
                nullable=False,
                server_default="borrador",
            ),
            sa.Column(
                "estado_dian",
                sa.String(40),
            ),
            sa.Column(
                "mensaje_dian",
                sa.String(500),
            ),
            sa.Column(
                "ruta_xml",
                sa.String(500),
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

        op.create_index(
            "ix_guia_remision_remision",
            "guias_remision_electronica",
            ["remision_id"],
        )

        op.create_table(
            "guia_remision_electronica_detalles",
            sa.Column(
                "id",
                sa.Integer(),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column(
                "guia_id",
                sa.Integer(),
                sa.ForeignKey(
                    "guias_remision_electronica.id",
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
        "guia_remision_electronica_detalles"
        in tablas
    ):

        op.drop_table(
            "guia_remision_electronica_detalles",
        )

    if "guias_remision_electronica" in tablas:

        op.drop_index(
            "ix_guia_remision_remision",
            table_name="guias_remision_electronica",
        )

        op.drop_table(
            "guias_remision_electronica",
        )
