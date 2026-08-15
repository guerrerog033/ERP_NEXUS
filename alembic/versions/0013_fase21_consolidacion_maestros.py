"""Fase 21 — consolidación maestros, roles tercero y trazabilidad documental."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0013_fase21_consolidacion"
down_revision: Union[str, None] = "0012_fase_e_logistica_reserva"
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

    tablas = set(
        sa.inspect(op.get_bind()).get_table_names(),
    )

    if "unidades_medida" not in tablas:

        op.create_table(
            "unidades_medida",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("codigo", sa.String(10), nullable=False, unique=True),
            sa.Column("nombre", sa.String(80), nullable=False),
            sa.Column("codigo_dian", sa.String(10)),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "fecha_actualizacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
        )

    if "formas_pago" not in tablas:

        op.create_table(
            "formas_pago",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("codigo", sa.String(20), nullable=False, unique=True),
            sa.Column("nombre", sa.String(120), nullable=False),
            sa.Column("dias_plazo", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "fecha_actualizacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
        )

    if "medios_pago" not in tablas:

        op.create_table(
            "medios_pago",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("codigo", sa.String(20), nullable=False, unique=True),
            sa.Column("nombre", sa.String(120), nullable=False),
            sa.Column("codigo_dian", sa.String(10)),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "fecha_actualizacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
        )

    if "vendedores" not in tablas:

        op.create_table(
            "vendedores",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("codigo", sa.String(20), nullable=False, unique=True),
            sa.Column("nombre", sa.String(120), nullable=False),
            sa.Column("tercero_id", sa.Integer(), sa.ForeignKey("terceros.id")),
            sa.Column("correo", sa.String(150)),
            sa.Column("telefono", sa.String(30)),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "fecha_actualizacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
        )

    if "atributos" not in tablas:

        op.create_table(
            "atributos",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("codigo", sa.String(30), nullable=False, unique=True),
            sa.Column("nombre", sa.String(80), nullable=False),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
        )

        op.create_table(
            "valores_atributo",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "atributo_id",
                sa.Integer(),
                sa.ForeignKey("atributos.id"),
                nullable=False,
            ),
            sa.Column("valor", sa.String(80), nullable=False),
            sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
            sa.UniqueConstraint(
                "atributo_id",
                "valor",
                name="uq_atributo_valor",
            ),
        )

    if "documento_vinculos" not in tablas:

        op.create_table(
            "documento_vinculos",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tipo_origen", sa.String(40), nullable=False),
            sa.Column("documento_origen_id", sa.Integer(), nullable=False),
            sa.Column("tipo_destino", sa.String(40), nullable=False),
            sa.Column("documento_destino_id", sa.Integer(), nullable=False),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.UniqueConstraint(
                "tipo_origen",
                "documento_origen_id",
                "tipo_destino",
                "documento_destino_id",
                name="uq_documento_vinculo",
            ),
        )

    if "numeracion_documentos" not in tablas:

        op.create_table(
            "numeracion_documentos",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("codigo_tipo", sa.String(40), nullable=False),
            sa.Column("prefijo", sa.String(10), nullable=False),
            sa.Column("resolucion", sa.String(80)),
            sa.Column("rango_desde", sa.Integer(), nullable=False, server_default="1"),
            sa.Column(
                "rango_hasta",
                sa.Integer(),
                nullable=False,
                server_default="999999",
            ),
            sa.Column(
                "consecutivo_actual",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.Column("fecha_inicio", sa.Date()),
            sa.Column("fecha_fin", sa.Date()),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "fecha_actualizacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
            sa.UniqueConstraint(
                "codigo_tipo",
                "prefijo",
                name="uq_numeracion_tipo_prefijo",
            ),
        )

    if "perfiles_cliente" not in tablas:

        op.create_table(
            "perfiles_cliente",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "tercero_id",
                sa.Integer(),
                sa.ForeignKey("terceros.id"),
                nullable=False,
                unique=True,
            ),
            sa.Column("codigo_cliente", sa.String(30), unique=True),
            sa.Column("zona", sa.String(80)),
            sa.Column("descuento", sa.Float(), nullable=False, server_default="0"),
            sa.Column("estado_cartera", sa.String(30), server_default="activo"),
            sa.Column("observaciones", sa.String(500)),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
        )

    if "perfiles_proveedor" not in tablas:

        op.create_table(
            "perfiles_proveedor",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "tercero_id",
                sa.Integer(),
                sa.ForeignKey("terceros.id"),
                nullable=False,
                unique=True,
            ),
            sa.Column("codigo_proveedor", sa.String(30), unique=True),
            sa.Column("cuenta_contable", sa.String(30)),
            sa.Column("banco", sa.String(120)),
            sa.Column("cuenta_bancaria", sa.String(50)),
            sa.Column("condiciones_comerciales", sa.String(500)),
            sa.Column("observaciones", sa.String(500)),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
        )

    if "tercero_direcciones" not in tablas:

        op.create_table(
            "tercero_direcciones",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "tercero_id",
                sa.Integer(),
                sa.ForeignKey("terceros.id"),
                nullable=False,
            ),
            sa.Column("etiqueta", sa.String(40), server_default="Principal"),
            sa.Column("direccion", sa.String(200)),
            sa.Column("ciudad", sa.String(100)),
            sa.Column("departamento", sa.String(100)),
            sa.Column("pais", sa.String(100)),
            sa.Column("principal", sa.Boolean(), nullable=False, server_default="false"),
        )

    if "tercero_contactos" not in tablas:

        op.create_table(
            "tercero_contactos",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "tercero_id",
                sa.Integer(),
                sa.ForeignKey("terceros.id"),
                nullable=False,
            ),
            sa.Column("nombre", sa.String(120), nullable=False),
            sa.Column("cargo", sa.String(80)),
            sa.Column("telefono", sa.String(30)),
            sa.Column("correo", sa.String(150)),
            sa.Column("principal", sa.Boolean(), nullable=False, server_default="false"),
        )

    if "empresa_bancos" not in tablas:

        op.create_table(
            "empresa_bancos",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "empresa_id",
                sa.Integer(),
                sa.ForeignKey("empresa.id"),
                nullable=False,
            ),
            sa.Column("banco", sa.String(120), nullable=False),
            sa.Column("tipo_cuenta", sa.String(30), server_default="Corriente"),
            sa.Column("numero_cuenta", sa.String(50), nullable=False),
            sa.Column("titular", sa.String(200)),
            sa.Column("activo", sa.Boolean(), server_default="true"),
            sa.Column(
                "fecha_creacion",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
            ),
        )

    columnas_terceros = _columnas("terceros")

    for columna, tipo in (
        ("es_cliente", sa.Boolean()),
        ("es_proveedor", sa.Boolean()),
        ("es_empleado", sa.Boolean()),
        ("es_vendedor", sa.Boolean()),
    ):

        if columna not in columnas_terceros:

            op.add_column(
                "terceros",
                sa.Column(
                    columna,
                    tipo,
                    nullable=False,
                    server_default="false",
                ),
            )

    if "vendedor_id" not in columnas_terceros:

        op.add_column(
            "terceros",
            sa.Column(
                "vendedor_id",
                sa.Integer(),
                sa.ForeignKey("vendedores.id"),
            ),
        )

    if "forma_pago_id" not in columnas_terceros:

        op.add_column(
            "terceros",
            sa.Column(
                "forma_pago_id",
                sa.Integer(),
                sa.ForeignKey("formas_pago.id"),
            ),
        )

    op.execute(
        sa.text(
            """
            UPDATE terceros SET es_cliente = true
            WHERE tipo_tercero = 'Cliente'
            """
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE terceros SET es_proveedor = true
            WHERE tipo_tercero = 'Proveedor'
            """
        ),
    )

    columnas_impuestos = _columnas("impuestos")

    if "cuenta_contable" not in columnas_impuestos:

        op.add_column(
            "impuestos",
            sa.Column("cuenta_contable", sa.String(30)),
        )

    if "codigo_dian" not in columnas_impuestos:

        op.add_column(
            "impuestos",
            sa.Column("codigo_dian", sa.String(10)),
        )

    columnas_bodegas = _columnas("bodegas")

    for columna, tipo in (
        ("direccion", sa.String(200)),
        ("ciudad", sa.String(100)),
        ("responsable", sa.String(120)),
    ):

        if columna not in columnas_bodegas:

            op.add_column(
                "bodegas",
                sa.Column(columna, tipo),
            )

    bind = op.get_bind()

    if bind.dialect.name == "postgresql":

        op.execute(
            sa.text(
                """
                INSERT INTO unidades_medida (codigo, nombre, codigo_dian)
                VALUES
                    ('UND', 'Unidad', '94'),
                    ('KG', 'Kilogramo', 'KGM'),
                    ('G', 'Gramo', 'GRM'),
                    ('MT', 'Metro', 'MTR'),
                    ('M2', 'Metro cuadrado', 'MTK'),
                    ('M3', 'Metro cúbico', 'MTQ'),
                    ('LT', 'Litro', 'LTR'),
                    ('HR', 'Hora', 'HUR'),
                    ('SERV', 'Servicio', '94')
                ON CONFLICT (codigo) DO NOTHING
                """
            ),
        )

        op.execute(
            sa.text(
                """
                INSERT INTO formas_pago (codigo, nombre, dias_plazo)
                VALUES
                    ('CONTADO', 'Contado', 0),
                    ('CRED30', 'Crédito 30 días', 30),
                    ('CRED60', 'Crédito 60 días', 60)
                ON CONFLICT (codigo) DO NOTHING
                """
            ),
        )

        op.execute(
            sa.text(
                """
                INSERT INTO medios_pago (codigo, nombre, codigo_dian)
                VALUES
                    ('EFECTIVO', 'Efectivo', '10'),
                    ('TRANSF', 'Transferencia', '47'),
                    ('TARJETA', 'Tarjeta', '48'),
                    ('PSE', 'PSE', '47'),
                    ('CHEQUE', 'Cheque', '20')
                ON CONFLICT (codigo) DO NOTHING
                """
            ),
        )


def downgrade() -> None:

    for tabla in (
        "empresa_bancos",
        "tercero_contactos",
        "tercero_direcciones",
        "perfiles_proveedor",
        "perfiles_cliente",
        "numeracion_documentos",
        "documento_vinculos",
        "valores_atributo",
        "atributos",
        "vendedores",
        "medios_pago",
        "formas_pago",
        "unidades_medida",
    ):

        op.execute(
            sa.text(
                f"DROP TABLE IF EXISTS {tabla} CASCADE",
            ),
        )

    columnas_terceros = _columnas("terceros")

    for columna in (
        "forma_pago_id",
        "vendedor_id",
        "es_vendedor",
        "es_empleado",
        "es_proveedor",
        "es_cliente",
    ):

        if columna in columnas_terceros:

            op.drop_column(
                "terceros",
                columna,
            )

    columnas_impuestos = _columnas("impuestos")

    for columna in (
        "codigo_dian",
        "cuenta_contable",
    ):

        if columna in columnas_impuestos:

            op.drop_column(
                "impuestos",
                columna,
            )

    columnas_bodegas = _columnas("bodegas")

    for columna in (
        "responsable",
        "ciudad",
        "direccion",
    ):

        if columna in columnas_bodegas:

            op.drop_column(
                "bodegas",
                columna,
            )
