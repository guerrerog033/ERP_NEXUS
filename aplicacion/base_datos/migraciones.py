from aplicacion.base_datos.admin import conexion_admin
from aplicacion.base_datos.locks import (
    liberar_locks_terceros,
)


def _tabla_existe(
    cur,
    tabla: str,
) -> bool:

    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = %s
        )
        """,
        (
            tabla,
        ),
    )

    return bool(
        cur.fetchone()[
            0
        ],
    )


def _columna_existe(
    cur,
    tabla: str,
    columna: str,
) -> bool:

    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
              AND column_name = %s
        )
        """,
        (
            tabla,
            columna,
        ),
    )

    return bool(
        cur.fetchone()[
            0
        ],
    )


def _aplicar_numeric_tablas(
    cur,
    tablas: dict,
) -> None:

    for tabla, columnas in tablas.items():

        if not _tabla_existe(
            cur,
            tabla,
        ):

            continue

        for columna, precision in columnas:

            if not _columna_existe(
                cur,
                tabla,
                columna,
            ):

                continue

            cur.execute(
                f"""
                ALTER TABLE {tabla}
                ALTER COLUMN {columna}
                TYPE NUMERIC({precision})
                USING {columna}::numeric({precision})
                """
            )


def migrar_terceros_fiscal() -> None:

    liberar_locks_terceros()

    alteraciones = [

        (
            "tipo_regimen_iva",
            "VARCHAR(80)",
            None,
        ),

        (
            "resp_o13",
            "BOOLEAN",
            "FALSE",
        ),

        (
            "resp_o15",
            "BOOLEAN",
            "FALSE",
        ),

        (
            "resp_o23",
            "BOOLEAN",
            "FALSE",
        ),

        (
            "resp_o47",
            "BOOLEAN",
            "FALSE",
        ),

        (
            "resp_r99_pn",
            "BOOLEAN",
            "TRUE",
        ),

        (
            "retefuente_id",
            "INTEGER",
            None,
        ),

        (
            "reteica_id",
            "INTEGER",
            None,
        ),

        (
            "reteiva_id",
            "INTEGER",
            None,
        ),

    ]

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        for (
            columna,
            tipo,
            defecto,
        ) in alteraciones:

            sql = (
                "ALTER TABLE terceros "
                f"ADD COLUMN IF NOT EXISTS {columna} "
                f"{tipo}"
            )

            if defecto is not None:

                sql += (
                    f" NOT NULL DEFAULT {defecto}"
                )

            cur.execute(sql)

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_productos() -> None:

    alteraciones = [

        (
            "codigo_barras",
            "VARCHAR(50)",
            None,
        ),

        (
            "impuesto_venta_id",
            "INTEGER",
            None,
        ),

        (
            "impuesto_compra_id",
            "INTEGER",
            None,
        ),

        (
            "precio_incluye_iva",
            "BOOLEAN",
            "FALSE",
        ),

    ]

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        for (
            columna,
            tipo,
            defecto,
        ) in alteraciones:

            sql = (
                "ALTER TABLE productos "
                f"ADD COLUMN IF NOT EXISTS {columna} "
                f"{tipo}"
            )

            if defecto is not None:

                sql += (
                    f" NOT NULL DEFAULT {defecto}"
                )

            cur.execute(sql)

        cur.execute("RESET lock_timeout")

        cur.execute(
            "ALTER TABLE producto_precios "
            "ADD COLUMN IF NOT EXISTS impuesto_id INTEGER"
        )

        cur.execute(
            "ALTER TABLE productos "
            "ADD COLUMN IF NOT EXISTS unidad_medida "
            "VARCHAR(10) NOT NULL DEFAULT 'Und'"
        )

        cur.close()

    finally:

        conexion.close()


def migrar_variantes_producto() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            "ALTER TABLE productos "
            "ADD COLUMN IF NOT EXISTS maneja_variantes "
            "BOOLEAN NOT NULL DEFAULT FALSE"
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS producto_variantes (
                id SERIAL PRIMARY KEY,
                producto_id INTEGER NOT NULL
                    REFERENCES productos(id),
                codigo VARCHAR(40) NOT NULL UNIQUE,
                codigo_barras VARCHAR(50) UNIQUE,
                talla VARCHAR(30),
                color VARCHAR(30),
                calibre VARCHAR(30),
                largo VARCHAR(30),
                precio_venta DOUBLE PRECISION,
                costo DOUBLE PRECISION,
                precio_incluye_iva BOOLEAN,
                impuesto_venta_id INTEGER
                    REFERENCES impuestos(id),
                impuesto_compra_id INTEGER
                    REFERENCES impuestos(id),
                imagen VARCHAR(500),
                existencia DOUBLE PRECISION NOT NULL DEFAULT 0,
                atributos JSONB NOT NULL DEFAULT '{}'::jsonb,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                orden INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cur.execute(
            "ALTER TABLE producto_variantes "
            "ADD COLUMN IF NOT EXISTS existencia "
            "DOUBLE PRECISION NOT NULL DEFAULT 0"
        )

        cur.execute(
            "ALTER TABLE producto_variantes "
            "ADD COLUMN IF NOT EXISTS atributos "
            "JSONB NOT NULL DEFAULT '{}'::jsonb"
        )

        for tabla in (
            "cotizacion_detalles",
            "orden_pedido_detalles",
            "factura_compra_detalles",
        ):
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = %s
                )
                """,
                (tabla,),
            )
            if not cur.fetchone()[0]:
                continue

            cur.execute(
                f"ALTER TABLE {tabla} "
                "ADD COLUMN IF NOT EXISTS "
                "producto_variante_id INTEGER"
            )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_catalogo_variantes() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS catalogo_variantes (
                id SERIAL PRIMARY KEY,
                tipo VARCHAR(30) NOT NULL,
                nombre_tipo VARCHAR(60) NOT NULL DEFAULT '',
                valor VARCHAR(80) NOT NULL,
                orden INTEGER NOT NULL DEFAULT 0,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
                CONSTRAINT uq_catalogo_variante_valor
                    UNIQUE (tipo, nombre_tipo, valor)
            )
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_cotizaciones() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            "ALTER TABLE cotizacion_detalles "
            "ADD COLUMN IF NOT EXISTS impuesto_id INTEGER"
        )

        cur.execute(
            "ALTER TABLE cotizacion_detalles "
            "ADD COLUMN IF NOT EXISTS precio_incluye_iva "
            "BOOLEAN NOT NULL DEFAULT FALSE"
        )

        cur.execute(
            "ALTER TABLE cotizacion_detalles "
            "ADD COLUMN IF NOT EXISTS retefuente_id INTEGER"
        )

        cur.execute(
            "ALTER TABLE cotizacion_detalles "
            "ADD COLUMN IF NOT EXISTS reteica_id INTEGER"
        )

        cur.execute(
            "ALTER TABLE cotizaciones "
            "ADD COLUMN IF NOT EXISTS retefuente_id INTEGER"
        )

        cur.execute(
            "ALTER TABLE cotizaciones "
            "ADD COLUMN IF NOT EXISTS reteica_id INTEGER"
        )

        cur.execute(
            "ALTER TABLE cotizaciones "
            "ADD COLUMN IF NOT EXISTS reteiva_id INTEGER"
        )

        cur.execute(
            "ALTER TABLE cotizaciones "
            "ADD COLUMN IF NOT EXISTS vendedor VARCHAR(120)"
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_terceros_comercial() -> None:

    alteraciones = [

        (
            "lista_precio_id",
            "INTEGER",
            None,
        ),

        (
            "dias_credito",
            "INTEGER",
            "0",
        ),

        (
            "cupo_credito",
            "DOUBLE PRECISION",
            "0",
        ),

        (
            "vendedor_asignado",
            "VARCHAR(120)",
            None,
        ),

    ]

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        for (
            columna,
            tipo,
            defecto,
        ) in alteraciones:

            sql = (
                "ALTER TABLE terceros "
                f"ADD COLUMN IF NOT EXISTS {columna} "
                f"{tipo}"
            )

            if defecto is not None:

                sql += (
                    f" NOT NULL DEFAULT {defecto}"
                )

            cur.execute(sql)

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_ventas_fase_d() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            "ALTER TABLE facturas_venta "
            "ADD COLUMN IF NOT EXISTS pedido_id INTEGER"
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_inventario_aplicado_documentos() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            "ALTER TABLE facturas_venta "
            "ADD COLUMN IF NOT EXISTS inventario_aplicado "
            "BOOLEAN NOT NULL DEFAULT FALSE"
        )

        cur.execute(
            "ALTER TABLE notas_credito_venta "
            "ADD COLUMN IF NOT EXISTS inventario_aplicado "
            "BOOLEAN NOT NULL DEFAULT FALSE"
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_contabilidad_venta() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            "ALTER TABLE facturas_venta "
            "ADD COLUMN IF NOT EXISTS contabilizado "
            "BOOLEAN NOT NULL DEFAULT FALSE"
        )

        cur.execute(
            "ALTER TABLE facturas_venta "
            "ADD COLUMN IF NOT EXISTS asiento_id INTEGER"
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_formato_impresion_venta() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            "ALTER TABLE facturas_venta "
            "ADD COLUMN IF NOT EXISTS formato_impresion "
            "VARCHAR(30) NOT NULL DEFAULT 'carta'"
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_atributos_variante_stock() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            "ALTER TABLE productos "
            "ADD COLUMN IF NOT EXISTS atributos_variante "
            "JSONB NOT NULL DEFAULT '[]'::jsonb"
        )

        cur.execute(
            "ALTER TABLE productos "
            "ADD COLUMN IF NOT EXISTS existencia "
            "DOUBLE PRECISION NOT NULL DEFAULT 0"
        )

        cur.execute(
            "ALTER TABLE producto_variantes "
            "ADD COLUMN IF NOT EXISTS existencia "
            "DOUBLE PRECISION NOT NULL DEFAULT 0"
        )

        cur.execute(
            "ALTER TABLE producto_variantes "
            "ADD COLUMN IF NOT EXISTS atributos "
            "JSONB NOT NULL DEFAULT '{}'::jsonb"
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_integracion_compras() -> None:

    alteraciones_factura = [

        (
            "cufe_validado",
            "BOOLEAN",
            "FALSE",
        ),

        (
            "cufe_estado_dian",
            "VARCHAR(40)",
            None,
        ),

        (
            "cufe_validado_en",
            "TIMESTAMP WITH TIME ZONE",
            None,
        ),

        (
            "cufe_mensaje_dian",
            "VARCHAR(500)",
            None,
        ),

        (
            "contabilizado",
            "BOOLEAN",
            "FALSE",
        ),

        (
            "asiento_id",
            "INTEGER",
            None,
        ),

    ]

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        for (
            columna,
            tipo,
            defecto,
        ) in alteraciones_factura:

            sql = (
                "ALTER TABLE facturas_compra "
                f"ADD COLUMN IF NOT EXISTS {columna} "
                f"{tipo}"
            )

            if defecto is not None:

                sql += (
                    f" NOT NULL DEFAULT {defecto}"
                )

            cur.execute(sql)

        cur.execute(
            "ALTER TABLE productos "
            "ADD COLUMN IF NOT EXISTS existencia "
            "DOUBLE PRECISION NOT NULL DEFAULT 0"
        )

        cur.execute(
            "ALTER TABLE factura_compra_detalles "
            "ADD COLUMN IF NOT EXISTS "
            "producto_variante_id INTEGER"
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_acuse_recibo_compras() -> None:

    alteraciones = [

        (
            "es_credito",
            "BOOLEAN",
            "FALSE",
        ),

        (
            "requiere_acuse_recibo",
            "BOOLEAN",
            "FALSE",
        ),

        (
            "acuse_recibo_estado",
            "VARCHAR(30)",
            "'no_aplica'",
        ),

        (
            "acuse_recibo_cude",
            "VARCHAR(100)",
            None,
        ),

        (
            "acuse_recibo_fecha",
            "TIMESTAMP WITH TIME ZONE",
            None,
        ),

        (
            "acuse_recibo_mensaje",
            "VARCHAR(500)",
            None,
        ),

        (
            "ruta_acuse_xml",
            "VARCHAR(500)",
            None,
        ),

    ]

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        for (
            columna,
            tipo,
            defecto,
        ) in alteraciones:

            sql = (
                "ALTER TABLE facturas_compra "
                f"ADD COLUMN IF NOT EXISTS {columna} "
                f"{tipo}"
            )

            if defecto is not None:

                sql += (
                    f" NOT NULL DEFAULT {defecto}"
                )

            cur.execute(sql)

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_auditoria() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS auditoria_eventos (
                id SERIAL PRIMARY KEY,
                fecha TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                usuario VARCHAR(50) NOT NULL DEFAULT 'sistema',
                accion VARCHAR(40) NOT NULL,
                modulo VARCHAR(60),
                entidad VARCHAR(80),
                entidad_id INTEGER,
                detalle TEXT,
                exito BOOLEAN NOT NULL DEFAULT TRUE
            )
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_auditoria_fecha
            ON auditoria_eventos (fecha DESC)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_auditoria_usuario
            ON auditoria_eventos (usuario)
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_auditoria_cambios() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS auditoria_cambios (
                id SERIAL PRIMARY KEY,
                fecha TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                usuario VARCHAR(50) NOT NULL DEFAULT 'sistema',
                modulo VARCHAR(60),
                entidad VARCHAR(80) NOT NULL,
                entidad_id INTEGER NOT NULL,
                campo VARCHAR(80) NOT NULL,
                valor_anterior TEXT,
                valor_nuevo TEXT
            )
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_auditoria_cambios_entidad
            ON auditoria_cambios (entidad, entidad_id)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_auditoria_cambios_fecha
            ON auditoria_cambios (fecha DESC)
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_numeric_core() -> None:

    conexion = conexion_admin()

    _TABLAS = {
        "facturas_venta": [
            ("subtotal", "18,2"),
            ("iva", "18,2"),
            ("valor_retefuente", "18,2"),
            ("valor_reteica", "18,2"),
            ("valor_reteiva", "18,2"),
            ("total", "18,2"),
            ("valor_pagado", "18,2"),
            ("saldo_pendiente", "18,2"),
        ],
        "factura_venta_detalles": [
            ("cantidad", "18,4"),
            ("precio_unitario", "18,2"),
            ("total_linea", "18,2"),
        ],
        "cotizaciones": [
            ("subtotal", "18,2"),
            ("total", "18,2"),
            ("descuento_porcentaje", "8,4"),
            ("descuento_valor", "18,2"),
        ],
        "cotizacion_detalles": [
            ("cantidad", "18,4"),
            ("precio_unitario", "18,2"),
            ("descuento_porcentaje", "8,4"),
            ("descuento_valor", "18,2"),
            ("total_linea", "18,2"),
        ],
    }

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        _aplicar_numeric_tablas(
            cur,
            _TABLAS,
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_numeric_modulos() -> None:

    conexion = conexion_admin()

    _TABLAS = {
        "proformas": [
            ("subtotal", "18,2"),
            ("total", "18,2"),
            ("tasa_cambio", "18,6"),
        ],
        "proforma_detalles": [
            ("cantidad", "18,4"),
            ("precio_unitario", "18,2"),
            ("descuento_porcentaje", "8,4"),
            ("total_linea", "18,2"),
        ],
        "ordenes_pedido": [
            ("subtotal", "18,2"),
            ("total", "18,2"),
        ],
        "orden_pedido_detalles": [
            ("cantidad", "18,4"),
            ("precio_unitario", "18,2"),
            ("total_linea", "18,2"),
        ],
        "remisiones_venta": [
            ("subtotal", "18,2"),
            ("total", "18,2"),
        ],
        "remision_venta_detalles": [
            ("cantidad", "18,4"),
            ("precio_unitario", "18,2"),
            ("total_linea", "18,2"),
        ],
        "notas_credito_venta": [
            ("subtotal", "18,2"),
            ("iva", "18,2"),
            ("valor_retefuente", "18,2"),
            ("valor_reteica", "18,2"),
            ("valor_reteiva", "18,2"),
            ("total", "18,2"),
        ],
        "nota_credito_venta_detalles": [
            ("cantidad", "18,4"),
            ("precio_unitario", "18,2"),
            ("total_linea", "18,2"),
        ],
        "notas_debito_venta": [
            ("subtotal", "18,2"),
            ("iva", "18,2"),
            ("valor_retefuente", "18,2"),
            ("valor_reteica", "18,2"),
            ("valor_reteiva", "18,2"),
            ("total", "18,2"),
        ],
        "nota_debito_venta_detalles": [
            ("cantidad", "18,4"),
            ("precio_unitario", "18,2"),
            ("total_linea", "18,2"),
        ],
        "documentos_soporte": [
            ("subtotal", "18,2"),
            ("iva", "18,2"),
            ("total", "18,2"),
        ],
        "documento_soporte_detalles": [
            ("cantidad", "18,4"),
            ("precio_unitario", "18,2"),
            ("total_linea", "18,2"),
        ],
        "facturas_compra": [
            ("subtotal", "18,2"),
            ("iva", "18,2"),
            ("valor_retefuente", "18,2"),
            ("valor_reteica", "18,2"),
            ("valor_reteiva", "18,2"),
            ("total", "18,2"),
            ("valor_pagado", "18,2"),
            ("saldo_pendiente", "18,2"),
        ],
        "factura_compra_detalles": [
            ("cantidad", "18,4"),
            ("precio_unitario", "18,2"),
            ("total_linea", "18,2"),
        ],
        "ordenes_compra": [
            ("subtotal", "18,2"),
            ("total", "18,2"),
        ],
        "orden_compra_detalles": [
            ("cantidad", "18,4"),
            ("cantidad_recibida", "18,4"),
            ("precio_unitario", "18,2"),
            ("total_linea", "18,2"),
        ],
        "recepcion_compra_detalles": [
            ("cantidad", "18,4"),
            ("costo_unitario", "18,2"),
        ],
        "cuentas_bancarias": [
            ("saldo", "18,2"),
        ],
        "lotes_pago": [
            ("total", "18,2"),
        ],
        "lote_pago_detalles": [
            ("valor", "18,2"),
        ],
        "recibos_caja": [
            ("total", "18,2"),
        ],
        "recibo_caja_detalles": [
            ("valor", "18,2"),
        ],
        "comprobantes_egreso": [
            ("total", "18,2"),
        ],
        "comprobante_egreso_detalles": [
            ("valor", "18,2"),
        ],
        "extractos_bancarios": [
            ("valor", "18,2"),
            ("saldo", "18,2"),
        ],
        "conciliaciones_bancarias": [
            ("valor", "18,2"),
        ],
    }

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        _aplicar_numeric_tablas(
            cur,
            _TABLAS,
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_numeric_fase5() -> None:

    conexion = conexion_admin()

    _TABLAS = {
        "asientos_contables": [
            ("total_debito", "18,2"),
            ("total_credito", "18,2"),
        ],
        "asiento_detalles": [
            ("debito", "18,2"),
            ("credito", "18,2"),
        ],
        "movimientos_inventario": [
            ("cantidad", "18,4"),
            ("costo_unitario", "18,2"),
        ],
        "crm_oportunidades": [
            ("valor_estimado", "18,2"),
            ("probabilidad", "8,4"),
        ],
        "nomina_empleados": [
            ("salario_basico", "18,2"),
            ("auxilio_transporte", "18,2"),
        ],
        "nomina_liquidaciones": [
            ("total_devengado", "18,2"),
            ("total_deducciones", "18,2"),
            ("neto_pagar", "18,2"),
            ("total_aportes_patronales", "18,2"),
        ],
        "nomina_liquidacion_conceptos": [
            ("valor", "18,2"),
        ],
        "nomina_contratos": [
            ("salario", "18,2"),
        ],
        "nomina_novedades": [
            ("cantidad", "18,4"),
            ("valor", "18,2"),
        ],
        "nomina_provisiones": [
            ("base", "18,2"),
            ("valor", "18,2"),
        ],
    }

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        _aplicar_numeric_tablas(
            cur,
            _TABLAS,
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_numeric_fase6() -> None:

    conexion = conexion_admin()

    _TABLAS = {
        "despachos_pedido": [
            ("latitud", "10,7"),
            ("longitud", "10,7"),
            ("costo_flete", "18,2"),
        ],
    }

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        _aplicar_numeric_tablas(
            cur,
            _TABLAS,
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pos_ventas_log (
                id SERIAL PRIMARY KEY,
                factura_id INTEGER NOT NULL
                    REFERENCES facturas_venta(id),
                total NUMERIC(18,2) NOT NULL DEFAULT 0,
                recibido NUMERIC(18,2) NOT NULL DEFAULT 0,
                cambio NUMERIC(18,2) NOT NULL DEFAULT 0,
                metodo_pago VARCHAR(30) NOT NULL DEFAULT 'efectivo',
                usuario VARCHAR(50) NOT NULL DEFAULT 'sistema',
                fecha_creacion TIMESTAMPTZ DEFAULT now()
            )
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_fase10_pos() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            ALTER TABLE productos
            ADD COLUMN IF NOT EXISTS stock_minimo DOUBLE PRECISION NOT NULL DEFAULT 0
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pos_cierres_caja (
                id SERIAL PRIMARY KEY,
                fecha DATE NOT NULL,
                usuario VARCHAR(50) NOT NULL DEFAULT 'sistema',
                efectivo_esperado NUMERIC(18,2) NOT NULL DEFAULT 0,
                efectivo_contado NUMERIC(18,2) NOT NULL DEFAULT 0,
                diferencia NUMERIC(18,2) NOT NULL DEFAULT 0,
                total_ventas NUMERIC(18,2) NOT NULL DEFAULT 0,
                ventas_count INTEGER NOT NULL DEFAULT 0,
                observaciones TEXT,
                fecha_cierre TIMESTAMPTZ DEFAULT now()
            )
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_pos_cierres_caja_fecha
            ON pos_cierres_caja (fecha)
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_fase_b_existencias_bodega() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS existencias_bodega (
                id SERIAL PRIMARY KEY,
                bodega_id INTEGER NOT NULL REFERENCES bodegas(id),
                producto_id INTEGER NOT NULL REFERENCES productos(id),
                producto_variante_id INTEGER REFERENCES producto_variantes(id),
                cantidad NUMERIC(18,4) NOT NULL DEFAULT 0
            )
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_existencias_bodega_bodega
            ON existencias_bodega (bodega_id)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_existencias_bodega_producto
            ON existencias_bodega (producto_id)
            """
        )

        cur.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_existencias_bodega_sin_variante
            ON existencias_bodega (bodega_id, producto_id)
            WHERE producto_variante_id IS NULL
            """
        )

        cur.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_existencias_bodega_con_variante
            ON existencias_bodega (bodega_id, producto_id, producto_variante_id)
            WHERE producto_variante_id IS NOT NULL
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()

    try:

        from aplicacion.modulos.inventario.servicios import (
            ServicioInventario,
        )

        ServicioInventario.sembrar_existencias_desde_productos()

    except Exception as error:

        print(
            "Advertencia: siembra existencias bodega: "
            f"{error}"
        )


def migrar_fase_c_ampliada() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            ALTER TABLE facturas_compra
            ADD COLUMN IF NOT EXISTS orden_compra_id INTEGER
            REFERENCES ordenes_compra(id)
            """
        )

        cur.execute(
            """
            ALTER TABLE facturas_compra
            ADD COLUMN IF NOT EXISTS inventario_aplicado BOOLEAN
            NOT NULL DEFAULT FALSE
            """
        )

        cur.execute(
            """
            ALTER TABLE facturas_compra
            ADD COLUMN IF NOT EXISTS match_estado VARCHAR(30)
            """
        )

        cur.execute(
            """
            ALTER TABLE facturas_compra
            ADD COLUMN IF NOT EXISTS match_mensaje VARCHAR(500)
            """
        )

        cur.execute(
            """
            ALTER TABLE factura_compra_detalles
            ADD COLUMN IF NOT EXISTS orden_detalle_id INTEGER
            REFERENCES orden_compra_detalles(id)
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_fase_c_complementos() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS factura_compra_eventos_radian (
                id SERIAL PRIMARY KEY,
                factura_id INTEGER NOT NULL
                    REFERENCES facturas_compra(id),
                codigo_evento VARCHAR(10) NOT NULL,
                cude VARCHAR(100),
                estado VARCHAR(30) NOT NULL DEFAULT 'enviado',
                mensaje VARCHAR(500),
                ruta_xml VARCHAR(500),
                forzado BOOLEAN NOT NULL DEFAULT FALSE,
                fecha_evento TIMESTAMPTZ DEFAULT NOW(),
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_fc_evento_radian_factura
            ON factura_compra_eventos_radian (factura_id)
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notas_credito_compra (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(30) NOT NULL UNIQUE,
                fecha DATE NOT NULL,
                proveedor_id INTEGER NOT NULL
                    REFERENCES terceros(id),
                factura_compra_id INTEGER NOT NULL
                    REFERENCES facturas_compra(id),
                motivo VARCHAR(250),
                factura_cufe VARCHAR(100),
                cufe VARCHAR(100),
                subtotal NUMERIC(18, 2) NOT NULL DEFAULT 0,
                iva NUMERIC(18, 2) NOT NULL DEFAULT 0,
                total NUMERIC(18, 2) NOT NULL DEFAULT 0,
                estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
                contabilizado BOOLEAN NOT NULL DEFAULT FALSE,
                inventario_aplicado BOOLEAN NOT NULL DEFAULT FALSE,
                asiento_id INTEGER
                    REFERENCES asientos_contables(id),
                observaciones TEXT,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS nota_credito_compra_detalles (
                id SERIAL PRIMARY KEY,
                nota_credito_id INTEGER NOT NULL
                    REFERENCES notas_credito_compra(id),
                producto_id INTEGER
                    REFERENCES productos(id),
                producto_variante_id INTEGER
                    REFERENCES producto_variantes(id),
                descripcion VARCHAR(250) NOT NULL,
                cantidad NUMERIC(18, 4) NOT NULL DEFAULT 1,
                precio_unitario NUMERIC(18, 2) NOT NULL DEFAULT 0,
                impuesto_id INTEGER
                    REFERENCES impuestos(id),
                precio_incluye_iva BOOLEAN NOT NULL DEFAULT FALSE,
                total_linea NUMERIC(18, 2) NOT NULL DEFAULT 0,
                orden INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_guias_remision_electronica() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS guias_remision_electronica (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(30) NOT NULL UNIQUE,
                prefijo VARCHAR(10),
                consecutivo_dian VARCHAR(20),
                fecha DATE NOT NULL,
                remision_id INTEGER
                    REFERENCES remisiones_venta(id),
                remision_numero VARCHAR(30),
                cliente_id INTEGER NOT NULL
                    REFERENCES terceros(id),
                subtotal NUMERIC(18, 2) NOT NULL DEFAULT 0,
                total NUMERIC(18, 2) NOT NULL DEFAULT 0,
                direccion_origen VARCHAR(250),
                ciudad_origen VARCHAR(80),
                departamento_origen VARCHAR(80),
                direccion_destino VARCHAR(250),
                ciudad_destino VARCHAR(80),
                departamento_destino VARCHAR(80),
                conductor VARCHAR(120),
                vehiculo VARCHAR(80),
                placa VARCHAR(20),
                transportadora VARCHAR(120),
                cude VARCHAR(100) UNIQUE,
                estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
                estado_dian VARCHAR(40),
                mensaje_dian VARCHAR(500),
                ruta_xml VARCHAR(500),
                observaciones TEXT,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_guia_remision_remision
            ON guias_remision_electronica (remision_id)
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS guia_remision_electronica_detalles (
                id SERIAL PRIMARY KEY,
                guia_id INTEGER NOT NULL
                    REFERENCES guias_remision_electronica(id),
                producto_id INTEGER
                    REFERENCES productos(id),
                producto_variante_id INTEGER
                    REFERENCES producto_variantes(id),
                descripcion VARCHAR(250) NOT NULL,
                cantidad NUMERIC(18, 4) NOT NULL DEFAULT 1,
                precio_unitario NUMERIC(18, 2) NOT NULL DEFAULT 0,
                total_linea NUMERIC(18, 2) NOT NULL DEFAULT 0,
                orden INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_fase_e_logistica_reserva() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            ALTER TABLE existencias_bodega
            ADD COLUMN IF NOT EXISTS cantidad_reservada
            NUMERIC(18, 4) NOT NULL DEFAULT 0
            """
        )

        cur.execute(
            """
            ALTER TABLE ordenes_pedido
            ADD COLUMN IF NOT EXISTS reserva_aplicada
            BOOLEAN NOT NULL DEFAULT FALSE
            """
        )

        cur.execute(
            """
            ALTER TABLE ordenes_pedido
            ADD COLUMN IF NOT EXISTS bodega_id INTEGER
            REFERENCES bodegas(id)
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS pedido_reservas (
                id SERIAL PRIMARY KEY,
                pedido_id INTEGER NOT NULL
                    REFERENCES ordenes_pedido(id),
                bodega_id INTEGER NOT NULL
                    REFERENCES bodegas(id),
                producto_id INTEGER NOT NULL
                    REFERENCES productos(id),
                producto_variante_id INTEGER
                    REFERENCES producto_variantes(id),
                cantidad NUMERIC(18, 4) NOT NULL DEFAULT 0,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_pedido_reservas_pedido
            ON pedido_reservas (pedido_id)
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_despacho_remision_id() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            ALTER TABLE despachos_pedido
            ADD COLUMN IF NOT EXISTS remision_id INTEGER
            REFERENCES remisiones_venta(id)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_despacho_remision_id
            ON despachos_pedido (remision_id)
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_roles_permisos() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                codigo VARCHAR(30) NOT NULL UNIQUE,
                nombre VARCHAR(100) NOT NULL,
                modulos JSONB NOT NULL DEFAULT '[]'::jsonb,
                activo BOOLEAN NOT NULL DEFAULT TRUE
            )
            """
        )

        cur.execute(
            "ALTER TABLE usuarios "
            "ADD COLUMN IF NOT EXISTS rol_id INTEGER"
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_licencias() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS licencias_activacion (
                id SERIAL PRIMARY KEY,
                serial VARCHAR(30) NOT NULL UNIQUE,
                edicion VARCHAR(30) NOT NULL,
                titular VARCHAR(200),
                nit_cliente VARCHAR(30),
                modulos JSONB NOT NULL DEFAULT '[]'::jsonb,
                max_usuarios INTEGER NOT NULL DEFAULT 1,
                fecha_activacion TIMESTAMP NOT NULL DEFAULT NOW(),
                fecha_vencimiento TIMESTAMP,
                huella_equipo VARCHAR(128) NOT NULL,
                estado VARCHAR(20) NOT NULL DEFAULT 'activa',
                activa BOOLEAN NOT NULL DEFAULT TRUE,
                notas TEXT
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS seriales_licencia (
                id SERIAL PRIMARY KEY,
                serial VARCHAR(30) NOT NULL UNIQUE,
                edicion VARCHAR(30) NOT NULL,
                modulos JSONB NOT NULL DEFAULT '[]'::jsonb,
                max_usuarios INTEGER NOT NULL DEFAULT 1,
                dias_validez INTEGER,
                titular_esperado VARCHAR(200),
                estado VARCHAR(20) NOT NULL DEFAULT 'disponible',
                fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
                activacion_id INTEGER
                    REFERENCES licencias_activacion(id)
            )
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_tesoreria() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        for tabla, columnas in (

            (
                "facturas_venta",
                [
                    (
                        "valor_pagado",
                        "DOUBLE PRECISION NOT NULL DEFAULT 0",
                    ),
                    (
                        "saldo_pendiente",
                        "DOUBLE PRECISION NOT NULL DEFAULT 0",
                    ),
                    (
                        "estado_pago",
                        "VARCHAR(20) NOT NULL DEFAULT 'pendiente'",
                    ),
                ],
            ),

            (
                "facturas_compra",
                [
                    (
                        "valor_pagado",
                        "DOUBLE PRECISION NOT NULL DEFAULT 0",
                    ),
                    (
                        "saldo_pendiente",
                        "DOUBLE PRECISION NOT NULL DEFAULT 0",
                    ),
                    (
                        "estado_pago",
                        "VARCHAR(20) NOT NULL DEFAULT 'pendiente'",
                    ),
                ],
            ),

        ):

            for (
                columna,
                tipo,
            ) in columnas:

                cur.execute(
                    f"ALTER TABLE {tabla} "
                    f"ADD COLUMN IF NOT EXISTS {columna} {tipo}"
                )

        cur.execute(
            """
            UPDATE facturas_venta
            SET saldo_pendiente = total - valor_pagado,
                estado_pago = CASE
                    WHEN valor_pagado <= 0 THEN 'pendiente'
                    WHEN valor_pagado >= total THEN 'pagada'
                    ELSE 'parcial'
                END
            WHERE total > 0
              AND saldo_pendiente = 0
              AND valor_pagado = 0
            """
        )

        cur.execute(
            """
            UPDATE facturas_compra
            SET saldo_pendiente = total - valor_pagado,
                estado_pago = CASE
                    WHEN valor_pagado <= 0 THEN 'pendiente'
                    WHEN valor_pagado >= total THEN 'pagada'
                    ELSE 'parcial'
                END
            WHERE total > 0
              AND saldo_pendiente = 0
              AND valor_pagado = 0
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS recibos_caja (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(30) NOT NULL UNIQUE,
                prefijo VARCHAR(10),
                fecha DATE NOT NULL,
                cliente_id INTEGER NOT NULL REFERENCES terceros(id),
                forma_pago VARCHAR(30) NOT NULL DEFAULT 'efectivo',
                valor_total DOUBLE PRECISION NOT NULL DEFAULT 0,
                estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
                contabilizado BOOLEAN NOT NULL DEFAULT FALSE,
                asiento_id INTEGER REFERENCES asientos_contables(id),
                observaciones TEXT,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS recibo_caja_detalles (
                id SERIAL PRIMARY KEY,
                recibo_id INTEGER NOT NULL
                    REFERENCES recibos_caja(id) ON DELETE CASCADE,
                factura_venta_id INTEGER NOT NULL
                    REFERENCES facturas_venta(id),
                valor_aplicado DOUBLE PRECISION NOT NULL DEFAULT 0,
                orden INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS comprobantes_egreso (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(30) NOT NULL UNIQUE,
                prefijo VARCHAR(10),
                fecha DATE NOT NULL,
                proveedor_id INTEGER NOT NULL REFERENCES terceros(id),
                forma_pago VARCHAR(30) NOT NULL DEFAULT 'transferencia',
                valor_total DOUBLE PRECISION NOT NULL DEFAULT 0,
                estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
                contabilizado BOOLEAN NOT NULL DEFAULT FALSE,
                asiento_id INTEGER REFERENCES asientos_contables(id),
                observaciones TEXT,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS comprobante_egreso_detalles (
                id SERIAL PRIMARY KEY,
                comprobante_id INTEGER NOT NULL
                    REFERENCES comprobantes_egreso(id) ON DELETE CASCADE,
                factura_compra_id INTEGER NOT NULL
                    REFERENCES facturas_compra(id),
                valor_aplicado DOUBLE PRECISION NOT NULL DEFAULT 0,
                orden INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_cartera() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        for tabla in (
            "facturas_venta",
            "facturas_compra",
        ):

            cur.execute(
                f"ALTER TABLE {tabla} "
                "ADD COLUMN IF NOT EXISTS "
                "fecha_vencimiento DATE"
            )

        cur.execute(
            """
            UPDATE facturas_venta fv
            SET fecha_vencimiento = fv.fecha + t.dias_credito
            FROM terceros t
            WHERE fv.cliente_id = t.id
              AND fv.fecha_vencimiento IS NULL
              AND fv.fecha IS NOT NULL
              AND COALESCE(t.dias_credito, 0) > 0
            """
        )

        cur.execute(
            """
            UPDATE facturas_venta
            SET fecha_vencimiento = fecha
            WHERE fecha_vencimiento IS NULL
              AND fecha IS NOT NULL
            """
        )

        cur.execute(
            """
            UPDATE facturas_compra fc
            SET fecha_vencimiento = fc.fecha + t.dias_credito
            FROM terceros t
            WHERE fc.proveedor_id = t.id
              AND fc.fecha_vencimiento IS NULL
              AND fc.fecha IS NOT NULL
              AND COALESCE(t.dias_credito, 0) > 0
            """
        )

        cur.execute(
            """
            UPDATE facturas_compra
            SET fecha_vencimiento = fecha
            WHERE fecha_vencimiento IS NULL
              AND fecha IS NOT NULL
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_compras_operativas() -> None:

    conexion = conexion_admin()

    try:

        cur = conexion.cursor()

        cur.execute("SET lock_timeout = '5s'")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ordenes_compra (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(30) UNIQUE NOT NULL,
                fecha DATE NOT NULL,
                proveedor_id INTEGER NOT NULL
                    REFERENCES terceros(id),
                observaciones TEXT,
                subtotal DOUBLE PRECISION NOT NULL DEFAULT 0,
                total DOUBLE PRECISION NOT NULL DEFAULT 0,
                estado VARCHAR(30) NOT NULL DEFAULT 'pendiente',
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS orden_compra_detalles (
                id SERIAL PRIMARY KEY,
                orden_id INTEGER NOT NULL
                    REFERENCES ordenes_compra(id) ON DELETE CASCADE,
                producto_id INTEGER
                    REFERENCES productos(id),
                producto_variante_id INTEGER
                    REFERENCES producto_variantes(id),
                descripcion VARCHAR(250) NOT NULL,
                cantidad DOUBLE PRECISION NOT NULL DEFAULT 1,
                cantidad_recibida DOUBLE PRECISION NOT NULL DEFAULT 0,
                costo_unitario DOUBLE PRECISION NOT NULL DEFAULT 0,
                total_linea DOUBLE PRECISION NOT NULL DEFAULT 0,
                linea_orden INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS recepciones_compra (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(30) UNIQUE NOT NULL,
                fecha DATE NOT NULL,
                orden_id INTEGER NOT NULL
                    REFERENCES ordenes_compra(id),
                bodega_id INTEGER NOT NULL
                    REFERENCES bodegas(id),
                observaciones TEXT,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS recepcion_compra_detalles (
                id SERIAL PRIMARY KEY,
                recepcion_id INTEGER NOT NULL
                    REFERENCES recepciones_compra(id) ON DELETE CASCADE,
                orden_detalle_id INTEGER NOT NULL
                    REFERENCES orden_compra_detalles(id),
                producto_id INTEGER
                    REFERENCES productos(id),
                producto_variante_id INTEGER
                    REFERENCES producto_variantes(id),
                cantidad DOUBLE PRECISION NOT NULL DEFAULT 0,
                costo_unitario DOUBLE PRECISION NOT NULL DEFAULT 0
            )
            """
        )

        cur.execute("RESET lock_timeout")

        cur.close()

    finally:

        conexion.close()


def migrar_fase4_ventas() -> None:

    conexion = conexion_admin()

    try:

        cursor = conexion.cursor()

        columnas_factura = (
            (
                "retefuente_id",
                "INTEGER REFERENCES impuestos(id)",
            ),
            (
                "reteica_id",
                "INTEGER REFERENCES impuestos(id)",
            ),
            (
                "reteiva_id",
                "INTEGER REFERENCES impuestos(id)",
            ),
            (
                "valor_retefuente",
                "DOUBLE PRECISION NOT NULL DEFAULT 0",
            ),
            (
                "valor_reteica",
                "DOUBLE PRECISION NOT NULL DEFAULT 0",
            ),
            (
                "valor_reteiva",
                "DOUBLE PRECISION NOT NULL DEFAULT 0",
            ),
        )

        for nombre, tipo in columnas_factura:

            cursor.execute(
                f"""
                ALTER TABLE facturas_venta
                ADD COLUMN IF NOT EXISTS
                {nombre} {tipo}
                """
            )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notas_credito_venta (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(30) UNIQUE NOT NULL,
                prefijo VARCHAR(10),
                consecutivo_dian VARCHAR(20),
                fecha DATE NOT NULL,
                cliente_id INTEGER NOT NULL
                    REFERENCES terceros(id),
                factura_id INTEGER NOT NULL
                    REFERENCES facturas_venta(id),
                motivo VARCHAR(250),
                factura_cufe VARCHAR(100),
                subtotal DOUBLE PRECISION NOT NULL DEFAULT 0,
                iva DOUBLE PRECISION NOT NULL DEFAULT 0,
                retefuente_id INTEGER
                    REFERENCES impuestos(id),
                reteica_id INTEGER
                    REFERENCES impuestos(id),
                reteiva_id INTEGER
                    REFERENCES impuestos(id),
                valor_retefuente DOUBLE PRECISION NOT NULL DEFAULT 0,
                valor_reteica DOUBLE PRECISION NOT NULL DEFAULT 0,
                valor_reteiva DOUBLE PRECISION NOT NULL DEFAULT 0,
                total DOUBLE PRECISION NOT NULL DEFAULT 0,
                cufe VARCHAR(100) UNIQUE,
                estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
                estado_dian VARCHAR(40),
                mensaje_dian VARCHAR(500),
                ruta_xml VARCHAR(500),
                ruta_zip VARCHAR(500),
                contabilizado BOOLEAN NOT NULL DEFAULT FALSE,
                asiento_id INTEGER
                    REFERENCES asientos_contables(id),
                observaciones TEXT,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nota_credito_venta_detalles (
                id SERIAL PRIMARY KEY,
                nota_credito_id INTEGER NOT NULL
                    REFERENCES notas_credito_venta(id)
                    ON DELETE CASCADE,
                producto_id INTEGER
                    REFERENCES productos(id),
                producto_variante_id INTEGER
                    REFERENCES producto_variantes(id),
                descripcion VARCHAR(250) NOT NULL,
                cantidad DOUBLE PRECISION NOT NULL DEFAULT 1,
                precio_unitario DOUBLE PRECISION NOT NULL DEFAULT 0,
                impuesto_id INTEGER
                    REFERENCES impuestos(id),
                precio_incluye_iva BOOLEAN NOT NULL DEFAULT FALSE,
                total_linea DOUBLE PRECISION NOT NULL DEFAULT 0,
                orden INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        conexion.commit()

    finally:

        conexion.close()


def migrar_fase4_complementos() -> None:

    conexion = conexion_admin()

    try:

        cursor = conexion.cursor()

        columnas_compra = (
            (
                "retefuente_id",
                "INTEGER REFERENCES impuestos(id)",
            ),
            (
                "reteica_id",
                "INTEGER REFERENCES impuestos(id)",
            ),
            (
                "reteiva_id",
                "INTEGER REFERENCES impuestos(id)",
            ),
            (
                "valor_retefuente",
                "DOUBLE PRECISION NOT NULL DEFAULT 0",
            ),
            (
                "valor_reteica",
                "DOUBLE PRECISION NOT NULL DEFAULT 0",
            ),
            (
                "valor_reteiva",
                "DOUBLE PRECISION NOT NULL DEFAULT 0",
            ),
            (
                "evento_radian_codigo",
                "VARCHAR(10)",
            ),
            (
                "evento_radian_cude",
                "VARCHAR(100)",
            ),
            (
                "evento_radian_mensaje",
                "VARCHAR(500)",
            ),
            (
                "evento_radian_fecha",
                "TIMESTAMPTZ",
            ),
        )

        for nombre, tipo in columnas_compra:

            cursor.execute(
                f"""
                ALTER TABLE facturas_compra
                ADD COLUMN IF NOT EXISTS
                {nombre} {tipo}
                """
            )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notas_debito_venta (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(30) UNIQUE NOT NULL,
                prefijo VARCHAR(10),
                consecutivo_dian VARCHAR(20),
                fecha DATE NOT NULL,
                cliente_id INTEGER NOT NULL
                    REFERENCES terceros(id),
                factura_id INTEGER NOT NULL
                    REFERENCES facturas_venta(id),
                motivo VARCHAR(250),
                factura_cufe VARCHAR(100),
                subtotal DOUBLE PRECISION NOT NULL DEFAULT 0,
                iva DOUBLE PRECISION NOT NULL DEFAULT 0,
                retefuente_id INTEGER
                    REFERENCES impuestos(id),
                reteica_id INTEGER
                    REFERENCES impuestos(id),
                reteiva_id INTEGER
                    REFERENCES impuestos(id),
                valor_retefuente DOUBLE PRECISION NOT NULL DEFAULT 0,
                valor_reteica DOUBLE PRECISION NOT NULL DEFAULT 0,
                valor_reteiva DOUBLE PRECISION NOT NULL DEFAULT 0,
                total DOUBLE PRECISION NOT NULL DEFAULT 0,
                cufe VARCHAR(100) UNIQUE,
                estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
                estado_dian VARCHAR(40),
                mensaje_dian VARCHAR(500),
                ruta_xml VARCHAR(500),
                ruta_zip VARCHAR(500),
                contabilizado BOOLEAN NOT NULL DEFAULT FALSE,
                asiento_id INTEGER
                    REFERENCES asientos_contables(id),
                observaciones TEXT,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nota_debito_venta_detalles (
                id SERIAL PRIMARY KEY,
                nota_debito_id INTEGER NOT NULL
                    REFERENCES notas_debito_venta(id)
                    ON DELETE CASCADE,
                producto_id INTEGER
                    REFERENCES productos(id),
                producto_variante_id INTEGER
                    REFERENCES producto_variantes(id),
                descripcion VARCHAR(250) NOT NULL,
                cantidad DOUBLE PRECISION NOT NULL DEFAULT 1,
                precio_unitario DOUBLE PRECISION NOT NULL DEFAULT 0,
                impuesto_id INTEGER
                    REFERENCES impuestos(id),
                precio_incluye_iva BOOLEAN NOT NULL DEFAULT FALSE,
                total_linea DOUBLE PRECISION NOT NULL DEFAULT 0,
                orden INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documentos_soporte (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(30) UNIQUE NOT NULL,
                prefijo VARCHAR(10),
                consecutivo_dian VARCHAR(20),
                fecha DATE NOT NULL,
                proveedor_id INTEGER
                    REFERENCES terceros(id),
                nit_proveedor VARCHAR(20),
                razon_social_proveedor VARCHAR(250),
                subtotal DOUBLE PRECISION NOT NULL DEFAULT 0,
                iva DOUBLE PRECISION NOT NULL DEFAULT 0,
                total DOUBLE PRECISION NOT NULL DEFAULT 0,
                cuds VARCHAR(100) UNIQUE,
                estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
                estado_dian VARCHAR(40),
                mensaje_dian VARCHAR(500),
                ruta_xml VARCHAR(500),
                observaciones TEXT,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documento_soporte_detalles (
                id SERIAL PRIMARY KEY,
                documento_id INTEGER NOT NULL
                    REFERENCES documentos_soporte(id)
                    ON DELETE CASCADE,
                descripcion VARCHAR(250) NOT NULL,
                cantidad DOUBLE PRECISION NOT NULL DEFAULT 1,
                precio_unitario DOUBLE PRECISION NOT NULL DEFAULT 0,
                impuesto_id INTEGER
                    REFERENCES impuestos(id),
                total_linea DOUBLE PRECISION NOT NULL DEFAULT 0,
                orden INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        conexion.commit()

    finally:

        conexion.close()


def ejecutar_migraciones() -> None:

    from aplicacion.base_datos.conexion import (
        probar_conexion,
    )

    try:

        probar_conexion()

    except RuntimeError as error:

        print(
            "Advertencia: migraciones omitidas: "
            f"{error}"
        )

        return

    try:

        migrar_terceros_fiscal()

    except Exception as error:

        print(
            "Advertencia: migración terceros fiscal: "
            f"{error}"
        )

    try:

        migrar_terceros_comercial()

    except Exception as error:

        print(
            "Advertencia: migración terceros comercial: "
            f"{error}"
        )

    try:

        migrar_productos()

    except Exception as error:

        print(
            "Advertencia: migración productos: "
            f"{error}"
        )

    try:

        migrar_variantes_producto()

    except Exception as error:

        print(
            "Advertencia: migración variantes producto: "
            f"{error}"
        )

    try:

        migrar_catalogo_variantes()

    except Exception as error:

        print(
            "Advertencia: migración catálogo variantes: "
            f"{error}"
        )

    try:

        migrar_atributos_variante_stock()

    except Exception as error:

        print(
            "Advertencia: migración atributos/stock variante: "
            f"{error}"
        )

    try:

        migrar_cotizaciones()

    except Exception as error:

        print(
            "Advertencia: migración cotizaciones: "
            f"{error}"
        )

    try:

        migrar_integracion_compras()

    except Exception as error:

        print(
            "Advertencia: migración integración compras: "
            f"{error}"
        )

    try:

        migrar_acuse_recibo_compras()

    except Exception as error:

        print(
            "Advertencia: migración acuse recibo compras: "
            f"{error}"
        )

    try:

        migrar_ventas_fase_d()

    except Exception as error:

        print(
            "Advertencia: migración ventas fase D: "
            f"{error}"
        )

    try:

        migrar_inventario_aplicado_documentos()

    except Exception as error:

        print(
            "Advertencia: migración inventario aplicado: "
            f"{error}"
        )

    try:

        migrar_contabilidad_venta()

    except Exception as error:

        print(
            "Advertencia: migración contabilidad venta: "
            f"{error}"
        )

    try:

        migrar_formato_impresion_venta()

    except Exception as error:

        print(
            "Advertencia: migración formato impresión venta: "
            f"{error}"
        )

    try:

        migrar_auditoria()

    except Exception as error:

        print(
            "Advertencia: migración auditoría: "
            f"{error}"
        )

    try:

        migrar_auditoria_cambios()

    except Exception as error:

        print(
            "Advertencia: migración auditoría campos: "
            f"{error}"
        )

    try:

        migrar_numeric_core()

    except Exception as error:

        print(
            "Advertencia: migración numeric core: "
            f"{error}"
        )

    try:

        migrar_numeric_modulos()

    except Exception as error:

        print(
            "Advertencia: migración numeric módulos: "
            f"{error}"
        )

    try:

        migrar_numeric_fase5()

    except Exception as error:

        print(
            "Advertencia: migración numeric fase 5: "
            f"{error}"
        )

    try:

        migrar_numeric_fase6()

    except Exception as error:

        print(
            "Advertencia: migración numeric fase 6: "
            f"{error}"
        )

    try:

        migrar_fase10_pos()

    except Exception as error:

        print(
            "Advertencia: migración fase 10 POS: "
            f"{error}"
        )

    try:

        migrar_fase_b_existencias_bodega()

    except Exception as error:

        print(
            "Advertencia: migración fase B existencias bodega: "
            f"{error}"
        )

    try:

        migrar_fase_c_ampliada()

    except Exception as error:

        print(
            "Advertencia: migración fase C ampliada: "
            f"{error}"
        )

    try:

        migrar_fase_c_complementos()

    except Exception as error:

        print(
            "Advertencia: migración fase C complementos: "
            f"{error}"
        )

    try:

        migrar_guias_remision_electronica()

    except Exception as error:

        print(
            "Advertencia: migración guías remisión electrónica: "
            f"{error}"
        )

    try:

        migrar_despacho_remision_id()

    except Exception as error:

        print(
            "Advertencia: migración despacho remision_id: "
            f"{error}"
        )

    try:

        migrar_fase_e_logistica_reserva()

    except Exception as error:

        print(
            "Advertencia: migración fase E logística/reserva: "
            f"{error}"
        )

    try:

        migrar_roles_permisos()

    except Exception as error:

        print(
            "Advertencia: migración roles/permisos: "
            f"{error}"
        )

    try:

        migrar_licencias()

    except Exception as error:

        print(
            "Advertencia: migración licencias: "
            f"{error}"
        )

    try:

        migrar_tesoreria()

    except Exception as error:

        print(
            "Advertencia: migración tesorería: "
            f"{error}"
        )

    try:

        migrar_cartera()

    except Exception as error:

        print(
            "Advertencia: migración cartera: "
            f"{error}"
        )

    try:

        migrar_compras_operativas()

    except Exception as error:

        print(
            "Advertencia: migración compras operativas: "
            f"{error}"
        )

    try:

        migrar_fase4_ventas()

    except Exception as error:

        print(
            "Advertencia: migración fase 4 ventas: "
            f"{error}"
        )

    try:

        migrar_fase4_complementos()

    except Exception as error:

        print(
            "Advertencia: migración fase 4 complementos: "
            f"{error}"
        )

    try:

        migrar_fase5_nomina()

    except Exception as error:

        print(
            "Advertencia: migración fase 5 nómina: "
            f"{error}"
        )

    try:

        migrar_fase5_nomina_complementos()

    except Exception as error:

        print(
            "Advertencia: migración fase 5 nómina complementos: "
            f"{error}"
        )

    try:

        migrar_fase5_nomina_profundizacion()

    except Exception as error:

        print(
            "Advertencia: migración fase 5 nómina profundización: "
            f"{error}"
        )

    try:

        migrar_fase6_crm()

    except Exception as error:

        print(
            "Advertencia: migración fase 6 CRM: "
            f"{error}"
        )

    try:

        migrar_fase7_enterprise()

    except Exception as error:

        print(
            "Advertencia: migración fase 7 enterprise: "
            f"{error}"
        )


def migrar_fase7_enterprise() -> None:
    conexion = conexion_admin()

    try:
        cursor = conexion.cursor()
        cursor.execute("SET lock_timeout = '5s'")

        cursor.execute(
            """
            ALTER TABLE cotizaciones
            ADD COLUMN IF NOT EXISTS fecha_vigencia DATE
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizaciones
            ADD COLUMN IF NOT EXISTS descuento_porcentaje DOUBLE PRECISION DEFAULT 0
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizaciones
            ADD COLUMN IF NOT EXISTS descuento_valor DOUBLE PRECISION DEFAULT 0
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizaciones
            ADD COLUMN IF NOT EXISTS condiciones_comerciales TEXT
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizaciones
            ADD COLUMN IF NOT EXISTS lista_precio_id INTEGER
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizaciones
            ADD COLUMN IF NOT EXISTS codigo_aceptacion VARCHAR(20)
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizaciones
            ADD COLUMN IF NOT EXISTS codigo_verificacion VARCHAR(20)
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizaciones
            ADD COLUMN IF NOT EXISTS estado_aceptacion VARCHAR(20) DEFAULT 'pendiente'
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizaciones
            ADD COLUMN IF NOT EXISTS firma_cliente VARCHAR(200)
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizacion_detalles
            ADD COLUMN IF NOT EXISTS descuento_porcentaje DOUBLE PRECISION DEFAULT 0
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizacion_detalles
            ADD COLUMN IF NOT EXISTS descuento_valor DOUBLE PRECISION DEFAULT 0
            """
        )
        cursor.execute(
            """
            ALTER TABLE cotizacion_detalles
            ADD COLUMN IF NOT EXISTS ficha_tecnica TEXT
            """
        )
        cursor.execute(
            """
            ALTER TABLE empresa
            ADD COLUMN IF NOT EXISTS logo_ruta VARCHAR(500)
            """
        )
        cursor.execute(
            """
            ALTER TABLE factura_compra_detalles
            ADD COLUMN IF NOT EXISTS codigo_referencia VARCHAR(80)
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reglas_contabilizacion (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(120) NOT NULL,
                tipo_operacion VARCHAR(40) NOT NULL DEFAULT 'compra',
                criterio VARCHAR(40) NOT NULL DEFAULT 'producto_tipo',
                valor_criterio VARCHAR(80) NOT NULL DEFAULT 'mercancia',
                cuenta_debito VARCHAR(20) NOT NULL,
                cuenta_credito VARCHAR(20),
                cuenta_iva VARCHAR(20),
                prioridad INTEGER NOT NULL DEFAULT 100,
                activo BOOLEAN NOT NULL DEFAULT TRUE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS extractos_bancarios (
                id SERIAL PRIMARY KEY,
                banco VARCHAR(120) NOT NULL,
                cuenta VARCHAR(40) NOT NULL,
                fecha DATE NOT NULL,
                descripcion VARCHAR(250),
                referencia VARCHAR(80),
                valor DOUBLE PRECISION NOT NULL DEFAULT 0,
                tipo VARCHAR(10) NOT NULL DEFAULT 'debito',
                saldo DOUBLE PRECISION,
                conciliado BOOLEAN NOT NULL DEFAULT FALSE,
                origen VARCHAR(40) DEFAULT 'importacion',
                fecha_creacion TIMESTAMPTZ DEFAULT now()
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conciliaciones_bancarias (
                id SERIAL PRIMARY KEY,
                extracto_id INTEGER NOT NULL
                    REFERENCES extractos_bancarios(id)
                    ON DELETE CASCADE,
                tipo_documento VARCHAR(30) NOT NULL,
                documento_id INTEGER NOT NULL,
                valor DOUBLE PRECISION NOT NULL,
                estado VARCHAR(20) DEFAULT 'conciliado',
                observaciones TEXT,
                fecha_creacion TIMESTAMPTZ DEFAULT now()
            )
            """
        )

        cursor.execute("RESET lock_timeout")
        conexion.commit()

    finally:
        conexion.close()


def migrar_fase5_nomina() -> None:

    conexion = conexion_admin()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nomina_empleados (
                id SERIAL PRIMARY KEY,
                codigo VARCHAR(20) UNIQUE NOT NULL,
                tipo_documento VARCHAR(20) NOT NULL DEFAULT 'CC',
                numero_documento VARCHAR(30) NOT NULL,
                dv VARCHAR(2),
                primer_nombre VARCHAR(100) NOT NULL,
                segundo_nombre VARCHAR(100),
                primer_apellido VARCHAR(100) NOT NULL,
                segundo_apellido VARCHAR(100),
                email VARCHAR(120),
                telefono VARCHAR(30),
                cargo VARCHAR(120),
                area VARCHAR(120),
                tipo_contrato VARCHAR(30) NOT NULL DEFAULT 'indefinido',
                salario_basico DOUBLE PRECISION NOT NULL DEFAULT 0,
                fecha_ingreso DATE,
                eps VARCHAR(120),
                afp VARCHAR(120),
                arl VARCHAR(120),
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT now()
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nomina_periodos (
                id SERIAL PRIMARY KEY,
                anio INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                estado VARCHAR(20) NOT NULL DEFAULT 'abierto',
                observaciones TEXT,
                fecha_liquidacion TIMESTAMPTZ,
                fecha_creacion TIMESTAMPTZ DEFAULT now(),
                UNIQUE (anio, mes)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nomina_liquidaciones (
                id SERIAL PRIMARY KEY,
                periodo_id INTEGER NOT NULL
                    REFERENCES nomina_periodos(id),
                empleado_id INTEGER NOT NULL
                    REFERENCES nomina_empleados(id),
                dias_trabajados INTEGER NOT NULL DEFAULT 30,
                total_devengado DOUBLE PRECISION NOT NULL DEFAULT 0,
                total_deducciones DOUBLE PRECISION NOT NULL DEFAULT 0,
                neto_pagar DOUBLE PRECISION NOT NULL DEFAULT 0,
                total_aportes_patronales DOUBLE PRECISION NOT NULL DEFAULT 0,
                fecha_creacion TIMESTAMPTZ DEFAULT now(),
                UNIQUE (periodo_id, empleado_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nomina_liquidacion_conceptos (
                id SERIAL PRIMARY KEY,
                liquidacion_id INTEGER NOT NULL
                    REFERENCES nomina_liquidaciones(id)
                    ON DELETE CASCADE,
                codigo VARCHAR(20) NOT NULL,
                nombre VARCHAR(120) NOT NULL,
                naturaleza VARCHAR(30) NOT NULL,
                valor DOUBLE PRECISION NOT NULL DEFAULT 0,
                orden INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        conexion.commit()

    finally:

        conexion.close()


def migrar_fase5_nomina_complementos() -> None:

    conexion = conexion_admin()

    try:

        cursor = conexion.cursor()

        for columna, definicion in (
            ("contabilizado", "BOOLEAN NOT NULL DEFAULT FALSE"),
            ("asiento_id", "INTEGER"),
            ("estado_dian", "VARCHAR(30) DEFAULT 'pendiente'"),
            ("cune", "VARCHAR(120)"),
            ("ruta_xml", "VARCHAR(500)"),
            ("ruta_pila", "VARCHAR(500)"),
        ):

            cursor.execute(
                f"""
                ALTER TABLE nomina_periodos
                ADD COLUMN IF NOT EXISTS {columna} {definicion}
                """
            )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nomina_contratos (
                id SERIAL PRIMARY KEY,
                empleado_id INTEGER NOT NULL
                    REFERENCES nomina_empleados(id),
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE,
                salario DOUBLE PRECISION NOT NULL DEFAULT 0,
                tipo_contrato VARCHAR(30) NOT NULL DEFAULT 'indefinido',
                cargo VARCHAR(120),
                observaciones TEXT,
                vigente BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT now()
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nomina_novedades (
                id SERIAL PRIMARY KEY,
                periodo_id INTEGER NOT NULL
                    REFERENCES nomina_periodos(id),
                empleado_id INTEGER NOT NULL
                    REFERENCES nomina_empleados(id),
                tipo VARCHAR(30) NOT NULL,
                cantidad DOUBLE PRECISION NOT NULL DEFAULT 0,
                valor DOUBLE PRECISION DEFAULT 0,
                observaciones TEXT,
                fecha_creacion TIMESTAMPTZ DEFAULT now()
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nomina_provisiones (
                id SERIAL PRIMARY KEY,
                periodo_id INTEGER NOT NULL
                    REFERENCES nomina_periodos(id),
                empleado_id INTEGER NOT NULL
                    REFERENCES nomina_empleados(id),
                tipo VARCHAR(30) NOT NULL,
                base DOUBLE PRECISION NOT NULL DEFAULT 0,
                valor DOUBLE PRECISION NOT NULL DEFAULT 0,
                estado VARCHAR(20) NOT NULL DEFAULT 'provisionado',
                fecha_creacion TIMESTAMPTZ DEFAULT now(),
                UNIQUE (periodo_id, empleado_id, tipo)
            )
            """
        )

        conexion.commit()

    finally:

        conexion.close()


def migrar_fase5_nomina_profundizacion() -> None:

    conexion = conexion_admin()

    try:

        cursor = conexion.cursor()

        for columna, definicion in (
            ("eps_codigo", "VARCHAR(6)"),
            ("afp_codigo", "VARCHAR(6)"),
            ("arl_codigo", "VARCHAR(6)"),
            ("auxilio_transporte", "DOUBLE PRECISION DEFAULT 0"),
            ("salario_integral", "BOOLEAN NOT NULL DEFAULT FALSE"),
            ("clase_riesgo", "VARCHAR(1) DEFAULT '1'"),
            ("centro_trabajo", "VARCHAR(9) DEFAULT '000000001'"),
            ("departamento_codigo", "VARCHAR(2) DEFAULT '11'"),
            ("municipio_codigo", "VARCHAR(3) DEFAULT '001'"),
        ):

            cursor.execute(
                f"""
                ALTER TABLE nomina_empleados
                ADD COLUMN IF NOT EXISTS {columna} {definicion}
                """
            )

        for columna, definicion in (
            ("mensaje_dian", "TEXT"),
            ("ruta_zip", "VARCHAR(500)"),
        ):

            cursor.execute(
                f"""
                ALTER TABLE nomina_periodos
                ADD COLUMN IF NOT EXISTS {columna} {definicion}
                """
            )

        conexion.commit()

    finally:

        conexion.close()


def migrar_fase6_crm() -> None:

    conexion = conexion_admin()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS crm_oportunidades (
                id SERIAL PRIMARY KEY,
                codigo VARCHAR(20) UNIQUE NOT NULL,
                titulo VARCHAR(200) NOT NULL,
                cliente_id INTEGER NOT NULL
                    REFERENCES terceros(id),
                etapa VARCHAR(30) NOT NULL DEFAULT 'prospeccion',
                valor_estimado DOUBLE PRECISION NOT NULL DEFAULT 0,
                probabilidad DOUBLE PRECISION NOT NULL DEFAULT 0,
                fecha_cierre_esperada DATE,
                observaciones TEXT,
                activo BOOLEAN NOT NULL DEFAULT TRUE,
                fecha_creacion TIMESTAMPTZ DEFAULT now()
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS crm_actividades (
                id SERIAL PRIMARY KEY,
                oportunidad_id INTEGER NOT NULL
                    REFERENCES crm_oportunidades(id)
                    ON DELETE CASCADE,
                tipo VARCHAR(30) NOT NULL DEFAULT 'tarea',
                titulo VARCHAR(200) NOT NULL,
                descripcion TEXT,
                fecha DATE NOT NULL,
                completada BOOLEAN NOT NULL DEFAULT FALSE,
                fecha_creacion TIMESTAMPTZ DEFAULT now()
            )
            """
        )

        conexion.commit()

    finally:

        conexion.close()
