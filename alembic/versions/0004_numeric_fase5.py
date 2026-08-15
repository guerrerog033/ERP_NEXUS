"""Revisiones Alembic — Fase 5: Numeric contabilidad/inventario/nómina/CRM."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from aplicacion.base_datos.alembic_numeric import (
    alterar_numeric,
)


revision: str = "0004_numeric_fase5"
down_revision: Union[str, None] = "0003_numeric_modulos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TABLAS_DINERO = {
    "asientos_contables": [
        "total_debito",
        "total_credito",
    ],
    "asiento_detalles": [
        "debito",
        "credito",
    ],
    "movimientos_inventario": [
        "costo_unitario",
    ],
    "crm_oportunidades": [
        "valor_estimado",
    ],
    "nomina_empleados": [
        "salario_basico",
        "auxilio_transporte",
    ],
    "nomina_liquidaciones": [
        "total_devengado",
        "total_deducciones",
        "neto_pagar",
        "total_aportes_patronales",
    ],
    "nomina_liquidacion_conceptos": [
        "valor",
    ],
    "nomina_contratos": [
        "salario",
    ],
    "nomina_novedades": [
        "valor",
    ],
    "nomina_provisiones": [
        "base",
        "valor",
    ],
}

_TABLAS_CANTIDAD = {
    "movimientos_inventario": [
        "cantidad",
    ],
    "nomina_novedades": [
        "cantidad",
    ],
}

_TABLAS_PORCENTAJE = {
    "crm_oportunidades": [
        "probabilidad",
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


def downgrade() -> None:

    todas: dict[str, list[str]] = {}

    for origen in (
        _TABLAS_DINERO,
        _TABLAS_CANTIDAD,
        _TABLAS_PORCENTAJE,
    ):

        for tabla, columnas in origen.items():

            todas.setdefault(
                tabla,
                [],
            ).extend(
                columnas,
            )

    for tabla, columnas in todas.items():

        for columna in columnas:

            op.alter_column(
                tabla,
                columna,
                type_=sa.Float(),
                postgresql_using=(
                    f"{columna}::double precision"
                ),
            )
