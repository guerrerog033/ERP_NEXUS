"""Revisiones Alembic del ERP NEXUS — Fase 3."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from aplicacion.base_datos.alembic_numeric import (
    alterar_numeric,
)


revision: str = "0002_numeric_auditoria_campos"
down_revision: Union[str, None] = "7c5b26130061"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TABLAS_DINERO = {
    "facturas_venta": [
        "subtotal",
        "iva",
        "valor_retefuente",
        "valor_reteica",
        "valor_reteiva",
        "total",
        "valor_pagado",
        "saldo_pendiente",
    ],
    "factura_venta_detalles": [
        "precio_unitario",
        "total_linea",
    ],
    "cotizaciones": [
        "subtotal",
        "total",
        "descuento_valor",
    ],
    "cotizacion_detalles": [
        "precio_unitario",
        "descuento_valor",
        "total_linea",
    ],
}

_TABLAS_CANTIDAD = {
    "factura_venta_detalles": [
        "cantidad",
    ],
    "cotizacion_detalles": [
        "cantidad",
    ],
}

_TABLAS_PORCENTAJE = {
    "cotizaciones": [
        "descuento_porcentaje",
    ],
    "cotizacion_detalles": [
        "descuento_porcentaje",
    ],
}


def upgrade() -> None:

    for tabla, columnas in _TABLAS_DINERO.items():

        alterar_numeric(
            {
                tabla: columnas,
            },
            18,
            2,
        )

    for tabla, columnas in _TABLAS_CANTIDAD.items():

        alterar_numeric(
            {
                tabla: columnas,
            },
            18,
            4,
        )

    for tabla, columnas in _TABLAS_PORCENTAJE.items():

        alterar_numeric(
            {
                tabla: columnas,
            },
            8,
            4,
        )

    bind = op.get_bind()
    inspector = sa.inspect(
        bind,
    )

    if (
        "auditoria_cambios"
        not in inspector.get_table_names()
    ):

        op.create_table(
            "auditoria_cambios",
            sa.Column(
                "id",
                sa.Integer(),
                autoincrement=True,
                nullable=False,
            ),
            sa.Column(
                "fecha",
                sa.DateTime(
                    timezone=True,
                ),
                server_default=sa.text(
                    "now()",
                ),
                nullable=False,
            ),
            sa.Column(
                "usuario",
                sa.String(
                    length=50,
                ),
                nullable=False,
                server_default="sistema",
            ),
            sa.Column(
                "modulo",
                sa.String(
                    length=60,
                ),
                nullable=True,
            ),
            sa.Column(
                "entidad",
                sa.String(
                    length=80,
                ),
                nullable=False,
            ),
            sa.Column(
                "entidad_id",
                sa.Integer(),
                nullable=False,
            ),
            sa.Column(
                "campo",
                sa.String(
                    length=80,
                ),
                nullable=False,
            ),
            sa.Column(
                "valor_anterior",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "valor_nuevo",
                sa.Text(),
                nullable=True,
            ),
            sa.PrimaryKeyConstraint(
                "id",
            ),
        )

        op.create_index(
            "idx_auditoria_cambios_entidad",
            "auditoria_cambios",
            [
                "entidad",
                "entidad_id",
            ],
        )

        op.create_index(
            "idx_auditoria_cambios_fecha",
            "auditoria_cambios",
            [
                "fecha",
            ],
            postgresql_ops={
                "fecha": "DESC",
            },
        )


def downgrade() -> None:

    op.drop_index(
        "idx_auditoria_cambios_fecha",
        table_name="auditoria_cambios",
    )

    op.drop_index(
        "idx_auditoria_cambios_entidad",
        table_name="auditoria_cambios",
    )

    op.drop_table(
        "auditoria_cambios",
    )

    for tabla, columnas in _TABLAS_PORCENTAJE.items():

        for columna in columnas:

            op.alter_column(
                tabla,
                columna,
                type_=sa.Float(),
                postgresql_using=(
                    f"{columna}::double precision"
                ),
            )

    for tabla, columnas in _TABLAS_CANTIDAD.items():

        for columna in columnas:

            op.alter_column(
                tabla,
                columna,
                type_=sa.Float(),
                postgresql_using=(
                    f"{columna}::double precision"
                ),
            )

    for tabla, columnas in _TABLAS_DINERO.items():

        for columna in columnas:

            op.alter_column(
                tabla,
                columna,
                type_=sa.Float(),
                postgresql_using=(
                    f"{columna}::double precision"
                ),
            )
