from __future__ import annotations

from datetime import date

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.productos.modelos import (
    Producto,
    ProductoVariante,
)
from aplicacion.maestros.terceros.modelos import Tercero
from aplicacion.nucleo.configuracion import Configuracion

from .modelos import AsientoContable, AsientoDetalle, PlanCuenta


class ServicioContabilidad:

    PLAN_INICIAL = (
        ("143501", "Mercancías no fabricadas", "activo"),
        ("240801", "IVA descontable", "activo"),
        ("220501", "Proveedores nacionales", "pasivo"),
        ("613501", "Compras de mercancía", "gasto"),
        ("413501", "Ingresos por ventas", "ingreso"),
        ("240805", "IVA generado", "pasivo"),
        ("130505", "Clientes nacionales", "activo"),
        ("613505", "Costo de ventas", "gasto"),
        ("110505", "Caja general", "activo"),
        ("111005", "Bancos", "activo"),
    )

    @classmethod
    def _cuenta(
        cls,
        clave: str,
        defecto: str,
    ) -> str:

        valor = Configuracion.obtener(
            "contabilidad",
            "cuentas",
            clave,
        )

        return str(
            valor or defecto,
        )

    @classmethod
    def _obtener_o_crear_cuenta(
        cls,
        db,
        codigo: str,
        nombre: str,
        tipo: str,
    ) -> PlanCuenta:

        cuenta = (
            db.query(PlanCuenta)
            .filter(
                PlanCuenta.codigo == codigo,
            )
            .first()
        )

        if cuenta is not None:

            return cuenta

        cuenta = PlanCuenta(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            activo=True,
        )

        db.add(cuenta)
        db.flush()

        return cuenta

    @classmethod
    def inicializar_plan(cls) -> None:

        db = SessionLocal()

        try:

            for (
                codigo,
                nombre,
                tipo,
            ) in cls.PLAN_INICIAL:

                existe = (
                    db.query(PlanCuenta)
                    .filter(
                        PlanCuenta.codigo == codigo,
                    )
                    .first()
                )

                if existe is None:

                    db.add(
                        PlanCuenta(
                            codigo=codigo,
                            nombre=nombre,
                            tipo=tipo,
                            activo=True,
                        ),
                    )

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def _siguiente_numero(cls, db) -> str:

        numeros = (
            db.query(AsientoContable.numero)
            .filter(
                AsientoContable.numero.like(
                    "AS%",
                ),
            )
            .all()
        )

        maximo = 0

        for (numero,) in numeros:

            sufijo = numero[2:]

            if sufijo.isdigit():

                maximo = max(
                    maximo,
                    int(sufijo),
                )

        return f"AS{maximo + 1:06d}"

    @classmethod
    def registrar_factura_compra(
        cls,
        factura,
    ) -> AsientoContable:

        cls.inicializar_plan()

        db = SessionLocal()

        try:

            cuenta_iva = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "iva_descontable",
                    "240801",
                ),
                "IVA descontable",
                "activo",
            )

            cuenta_cxp = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "cuentas_por_pagar",
                    "220501",
                ),
                "Proveedores nacionales",
                "pasivo",
            )

            from aplicacion.modulos.contabilidad.reglas.servicio_reglas import (
                ServicioReglasContabilizacion,
            )

            bases_por_cuenta: dict[str, float] = {}

            for detalle in factura.detalles:

                monto = float(
                    detalle.total_linea or 0,
                )

                producto = None

                if detalle.producto_id:
                    producto = (
                        db.query(Producto)
                        .filter(
                            Producto.id
                            == detalle.producto_id,
                        )
                        .first()
                    )

                cuentas = (
                    ServicioReglasContabilizacion
                    .resolver_cuentas_compra(
                        producto_tipo=(
                            producto.tipo
                            if producto
                            else None
                        ),
                        tiene_producto=bool(
                            detalle.producto_id,
                        ),
                    )
                )

                codigo_debito = cuentas["debito"]

                bases_por_cuenta[codigo_debito] = (
                    bases_por_cuenta.get(
                        codigo_debito,
                        0.0,
                    )
                    + monto
                )

            cuentas_debito: dict[str, float] = bases_por_cuenta

            iva = float(
                factura.iva or 0,
            )

            total = float(
                factura.total or 0,
            )

            asiento = AsientoContable(
                numero=cls._siguiente_numero(
                    db,
                ),
                fecha=factura.fecha or date.today(),
                descripcion=(
                    f"Factura compra "
                    f"{factura.numero}"
                ),
                origen="factura_compra",
                origen_id=factura.id,
            )

            db.add(asiento)
            db.flush()

            lineas: list[dict] = []
            orden = 0

            for codigo_cuenta, monto in cuentas_debito.items():
                if monto <= 0:
                    continue

                cuenta = cls._obtener_o_crear_cuenta(
                    db,
                    codigo_cuenta,
                    "Cuenta compra",
                    "activo"
                    if codigo_cuenta.startswith(
                        ("1", "2"),
                    )
                    else "gasto",
                )

                lineas.append(
                    {
                        "cuenta_id": cuenta.id,
                        "debito": monto,
                        "credito": 0,
                        "descripcion": (
                            "Compra "
                            f"{codigo_cuenta}"
                        ),
                        "orden": orden,
                    },
                )

                orden += 1

            if iva > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_iva.id,
                        "debito": iva,
                        "credito": 0,
                        "descripcion": "IVA descontable",
                        "orden": orden,
                    },
                )

                orden += 1

            lineas.append(
                {
                    "cuenta_id": cuenta_cxp.id,
                    "debito": 0,
                    "credito": total,
                    "descripcion": (
                        factura.razon_social_proveedor
                        or "Proveedor"
                    ),
                    "orden": orden,
                },
            )

            retenciones = (
                (
                    "retencion_retefuente_compra",
                    "23654001",
                    "Retención retefuente por pagar",
                    float(
                        getattr(
                            factura,
                            "valor_retefuente",
                            0,
                        )
                        or 0,
                    ),
                ),
                (
                    "retencion_reteica_compra",
                    "23680501",
                    "Retención ICA por pagar",
                    float(
                        getattr(
                            factura,
                            "valor_reteica",
                            0,
                        )
                        or 0,
                    ),
                ),
                (
                    "retencion_reteiva_compra",
                    "23680101",
                    "Retención IVA por pagar",
                    float(
                        getattr(
                            factura,
                            "valor_reteiva",
                            0,
                        )
                        or 0,
                    ),
                ),
            )

            for (
                clave,
                codigo,
                nombre,
                valor,
            ) in retenciones:

                if valor <= 0:

                    continue

                cuenta_ret = cls._obtener_o_crear_cuenta(
                    db,
                    cls._cuenta(
                        clave,
                        codigo,
                    ),
                    nombre,
                    "pasivo",
                )

                lineas.append(
                    {
                        "cuenta_id": cuenta_ret.id,
                        "debito": 0,
                        "credito": valor,
                        "descripcion": nombre,
                        "orden": orden,
                    },
                )

                orden += 1

            total_debito = 0.0
            total_credito = 0.0

            for linea in lineas:

                db.add(
                    AsientoDetalle(
                        asiento_id=asiento.id,
                        **linea,
                    ),
                )

                total_debito += float(
                    linea["debito"],
                )

                total_credito += float(
                    linea["credito"],
                )

            asiento.total_debito = total_debito
            asiento.total_credito = total_credito

            db.commit()
            db.refresh(asiento)

            return asiento

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def registrar_recibo_caja(
        cls,
        recibo,
    ) -> AsientoContable:

        cls.inicializar_plan()

        db = SessionLocal()

        try:

            cuenta_caja = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "caja",
                    "110505",
                ),
                "Caja general",
                "activo",
            )

            cuenta_cxc = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "cuentas_por_cobrar",
                    "130505",
                ),
                "Clientes nacionales",
                "activo",
            )

            from aplicacion.modulos.ventas.facturas.modelos import (
                FacturaVenta,
            )

            total = float(
                recibo.valor_total or 0,
            )

            asiento = AsientoContable(
                numero=cls._siguiente_numero(
                    db,
                ),
                fecha=recibo.fecha or date.today(),
                descripcion=(
                    f"Recibo de caja "
                    f"{recibo.numero}"
                ),
                origen="recibo_caja",
                origen_id=recibo.id,
            )

            db.add(asiento)
            db.flush()

            lineas: list[dict] = []
            orden = 0

            if total > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_caja.id,
                        "debito": total,
                        "credito": 0,
                        "descripcion": (
                            f"Pago {recibo.forma_pago}"
                        ),
                        "orden": orden,
                    },
                )

                orden += 1

            for detalle in recibo.detalles:

                factura = (
                    db.query(FacturaVenta)
                    .filter(
                        FacturaVenta.id
                        == detalle.factura_venta_id,
                    )
                    .first()
                )

                valor = float(
                    detalle.valor_aplicado or 0,
                )

                if valor <= 0:

                    continue

                descripcion = (
                    factura.numero
                    if factura is not None
                    else "Factura venta"
                )

                lineas.append(
                    {
                        "cuenta_id": cuenta_cxc.id,
                        "debito": 0,
                        "credito": valor,
                        "descripcion": descripcion,
                        "orden": orden,
                    },
                )

                orden += 1

            if (
                total > 0
                and not recibo.detalles
            ):

                cuenta_anticipos = cls._obtener_o_crear_cuenta(
                    db,
                    cls._cuenta(
                        "anticipos_clientes",
                        "280505",
                    ),
                    "Anticipos de clientes",
                    "pasivo",
                )

                lineas.append(
                    {
                        "cuenta_id": cuenta_anticipos.id,
                        "debito": 0,
                        "credito": total,
                        "descripcion": (
                            "Abono / anticipo cliente"
                        ),
                        "orden": orden,
                    },
                )

                orden += 1

            total_debito = 0.0
            total_credito = 0.0

            for linea in lineas:

                db.add(
                    AsientoDetalle(
                        asiento_id=asiento.id,
                        **linea,
                    ),
                )

                total_debito += float(
                    linea["debito"],
                )

                total_credito += float(
                    linea["credito"],
                )

            asiento.total_debito = total_debito
            asiento.total_credito = total_credito

            db.commit()
            db.refresh(asiento)

            return asiento

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def registrar_comprobante_egreso(
        cls,
        comprobante,
    ) -> AsientoContable:

        cls.inicializar_plan()

        db = SessionLocal()

        try:

            cuenta_caja = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "caja",
                    "110505",
                ),
                "Caja general",
                "activo",
            )

            cuenta_cxp = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "cuentas_por_pagar",
                    "220501",
                ),
                "Proveedores nacionales",
                "pasivo",
            )

            from aplicacion.modulos.compras.facturas.modelos import (
                FacturaCompra,
            )

            total = float(
                comprobante.valor_total or 0,
            )

            asiento = AsientoContable(
                numero=cls._siguiente_numero(
                    db,
                ),
                fecha=comprobante.fecha or date.today(),
                descripcion=(
                    f"Comprobante de egreso "
                    f"{comprobante.numero}"
                ),
                origen="comprobante_egreso",
                origen_id=comprobante.id,
            )

            db.add(asiento)
            db.flush()

            lineas: list[dict] = []
            orden = 0

            if (
                total > 0
                and not comprobante.detalles
            ):

                cuenta_anticipos = cls._obtener_o_crear_cuenta(
                    db,
                    cls._cuenta(
                        "anticipos_proveedores",
                        "133005",
                    ),
                    "Anticipos a proveedores",
                    "activo",
                )

                lineas.append(
                    {
                        "cuenta_id": cuenta_anticipos.id,
                        "debito": total,
                        "credito": 0,
                        "descripcion": (
                            "Anticipo a proveedor"
                        ),
                        "orden": orden,
                    },
                )

                orden += 1

            for detalle in comprobante.detalles:

                factura = (
                    db.query(FacturaCompra)
                    .filter(
                        FacturaCompra.id
                        == detalle.factura_compra_id,
                    )
                    .first()
                )

                valor = float(
                    detalle.valor_aplicado or 0,
                )

                if valor <= 0:

                    continue

                descripcion = (
                    factura.numero
                    if factura is not None
                    else "Factura compra"
                )

                lineas.append(
                    {
                        "cuenta_id": cuenta_cxp.id,
                        "debito": valor,
                        "credito": 0,
                        "descripcion": descripcion,
                        "orden": orden,
                    },
                )

                orden += 1

            if total > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_caja.id,
                        "debito": 0,
                        "credito": total,
                        "descripcion": (
                            f"Pago {comprobante.forma_pago}"
                        ),
                        "orden": orden,
                    },
                )

            total_debito = 0.0
            total_credito = 0.0

            for linea in lineas:

                db.add(
                    AsientoDetalle(
                        asiento_id=asiento.id,
                        **linea,
                    ),
                )

                total_debito += float(
                    linea["debito"],
                )

                total_credito += float(
                    linea["credito"],
                )

            asiento.total_debito = total_debito
            asiento.total_credito = total_credito

            db.commit()
            db.refresh(asiento)

            return asiento

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def registrar_factura_venta(
        cls,
        factura,
    ) -> AsientoContable:

        cls.inicializar_plan()

        db = SessionLocal()

        try:

            cuenta_cxc = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "cuentas_por_cobrar",
                    "130505",
                ),
                "Clientes nacionales",
                "activo",
            )

            cuenta_ingresos = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "ingresos",
                    "413501",
                ),
                "Ingresos por ventas",
                "ingreso",
            )

            cuenta_iva = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "iva_generado",
                    "240805",
                ),
                "IVA generado",
                "pasivo",
            )

            cuenta_inventario = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "inventario",
                    "143501",
                ),
                "Mercancías no fabricadas",
                "activo",
            )

            cuenta_costo = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "costo_ventas",
                    "613505",
                ),
                "Costo de ventas",
                "gasto",
            )

            cliente = (
                db.query(Tercero)
                .filter(
                    Tercero.id == factura.cliente_id,
                )
                .first()
            )

            nombre_cliente = "Cliente"

            if cliente is not None:

                nombre_cliente = (
                    cliente.razon_social
                    or cliente.nombre_completo
                    or cliente.numero_documento
                    or nombre_cliente
                )

            total = float(
                factura.total or 0,
            )

            iva = float(
                factura.iva or 0,
            )

            base_ingresos = max(
                total - iva,
                0.0,
            )

            costo_total = 0.0

            for detalle in factura.detalles:

                if not detalle.producto_id:

                    continue

                producto = (
                    db.query(Producto)
                    .filter(
                        Producto.id
                        == detalle.producto_id,
                    )
                    .first()
                )

                if (
                    producto is None
                    or producto.tipo == "servicio"
                ):

                    continue

                cantidad = float(
                    detalle.cantidad or 0,
                )

                if cantidad <= 0:

                    continue

                costo_unitario = float(
                    producto.costo or 0,
                )

                if detalle.producto_variante_id:

                    variante = (
                        db.query(ProductoVariante)
                        .filter(
                            ProductoVariante.id
                            == detalle.producto_variante_id,
                        )
                        .first()
                    )

                    if (
                        variante is not None
                        and variante.costo is not None
                    ):

                        costo_unitario = float(
                            variante.costo,
                        )

                costo_total += (
                    costo_unitario * cantidad
                )

            asiento = AsientoContable(
                numero=cls._siguiente_numero(
                    db,
                ),
                fecha=factura.fecha or date.today(),
                descripcion=(
                    f"Factura venta "
                    f"{factura.numero}"
                ),
                origen="factura_venta",
                origen_id=factura.id,
            )

            db.add(asiento)
            db.flush()

            lineas: list[dict] = []
            orden = 0

            if total > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_cxc.id,
                        "debito": total,
                        "credito": 0,
                        "descripcion": nombre_cliente,
                        "orden": orden,
                    },
                )

                orden += 1

            if base_ingresos > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_ingresos.id,
                        "debito": 0,
                        "credito": base_ingresos,
                        "descripcion": "Ingresos por venta",
                        "orden": orden,
                    },
                )

                orden += 1

            if iva > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_iva.id,
                        "debito": 0,
                        "credito": iva,
                        "descripcion": "IVA generado",
                        "orden": orden,
                    },
                )

                orden += 1

            retenciones = (
                (
                    "retencion_retefuente",
                    "13551515",
                    "Retención en la fuente",
                    float(
                        getattr(
                            factura,
                            "valor_retefuente",
                            0,
                        )
                        or 0,
                    ),
                ),
                (
                    "retencion_reteica",
                    "13551801",
                    "Retención ICA",
                    float(
                        getattr(
                            factura,
                            "valor_reteica",
                            0,
                        )
                        or 0,
                    ),
                ),
                (
                    "retencion_reteiva",
                    "13552001",
                    "Retención IVA",
                    float(
                        getattr(
                            factura,
                            "valor_reteiva",
                            0,
                        )
                        or 0,
                    ),
                ),
            )

            for (
                clave,
                codigo,
                nombre,
                valor,
            ) in retenciones:

                if valor <= 0:

                    continue

                cuenta_ret = cls._obtener_o_crear_cuenta(
                    db,
                    cls._cuenta(
                        clave,
                        codigo,
                    ),
                    nombre,
                    "activo",
                )

                lineas.append(
                    {
                        "cuenta_id": cuenta_ret.id,
                        "debito": valor,
                        "credito": 0,
                        "descripcion": nombre,
                        "orden": orden,
                    },
                )

                orden += 1

            if costo_total > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_costo.id,
                        "debito": costo_total,
                        "credito": 0,
                        "descripcion": "Costo de mercancía vendida",
                        "orden": orden,
                    },
                )

                orden += 1

                lineas.append(
                    {
                        "cuenta_id": cuenta_inventario.id,
                        "debito": 0,
                        "credito": costo_total,
                        "descripcion": "Salida inventario",
                        "orden": orden,
                    },
                )

            total_debito = 0.0
            total_credito = 0.0

            for linea in lineas:

                db.add(
                    AsientoDetalle(
                        asiento_id=asiento.id,
                        **linea,
                    ),
                )

                total_debito += float(
                    linea["debito"],
                )

                total_credito += float(
                    linea["credito"],
                )

            asiento.total_debito = total_debito
            asiento.total_credito = total_credito

            db.commit()
            db.refresh(asiento)

            return asiento

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def registrar_nota_credito_venta(
        cls,
        nota,
    ) -> AsientoContable:

        cls.inicializar_plan()

        db = SessionLocal()

        try:

            cuenta_cxc = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "cuentas_por_cobrar",
                    "130505",
                ),
                "Clientes nacionales",
                "activo",
            )

            cuenta_ingresos = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "ingresos",
                    "413501",
                ),
                "Ingresos por ventas",
                "ingreso",
            )

            cuenta_iva = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "iva_generado",
                    "240805",
                ),
                "IVA generado",
                "pasivo",
            )

            cliente = (
                db.query(Tercero)
                .filter(
                    Tercero.id == nota.cliente_id,
                )
                .first()
            )

            nombre_cliente = "Cliente"

            if cliente is not None:

                nombre_cliente = (
                    cliente.nombre_comercial
                    or cliente.razon_social
                    or cliente.nombre_completo
                    or cliente.numero_documento
                    or nombre_cliente
                )

            total = float(
                nota.total or 0,
            )

            iva = float(
                nota.iva or 0,
            )

            base_ingresos = float(
                nota.subtotal or 0,
            )

            asiento = AsientoContable(
                numero=cls._siguiente_numero(
                    db,
                ),
                fecha=nota.fecha or date.today(),
                descripcion=(
                    f"Nota crédito venta "
                    f"{nota.numero}"
                ),
                origen="nota_credito_venta",
                origen_id=nota.id,
            )

            db.add(asiento)
            db.flush()

            lineas: list[dict] = []
            orden = 0

            if total > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_cxc.id,
                        "debito": 0,
                        "credito": total,
                        "descripcion": nombre_cliente,
                        "orden": orden,
                    },
                )

                orden += 1

            if base_ingresos > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_ingresos.id,
                        "debito": base_ingresos,
                        "credito": 0,
                        "descripcion": "Reverso ingresos",
                        "orden": orden,
                    },
                )

                orden += 1

            if iva > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_iva.id,
                        "debito": iva,
                        "credito": 0,
                        "descripcion": "Reverso IVA generado",
                        "orden": orden,
                    },
                )

                orden += 1

            retenciones = (
                (
                    "retencion_retefuente",
                    "13551515",
                    "Reverso retención en la fuente",
                    float(
                        getattr(
                            nota,
                            "valor_retefuente",
                            0,
                        )
                        or 0,
                    ),
                ),
                (
                    "retencion_reteica",
                    "13551801",
                    "Reverso retención ICA",
                    float(
                        getattr(
                            nota,
                            "valor_reteica",
                            0,
                        )
                        or 0,
                    ),
                ),
                (
                    "retencion_reteiva",
                    "13552001",
                    "Reverso retención IVA",
                    float(
                        getattr(
                            nota,
                            "valor_reteiva",
                            0,
                        )
                        or 0,
                    ),
                ),
            )

            for (
                clave,
                codigo,
                nombre,
                valor,
            ) in retenciones:

                if valor <= 0:

                    continue

                cuenta_ret = cls._obtener_o_crear_cuenta(
                    db,
                    cls._cuenta(
                        clave,
                        codigo,
                    ),
                    nombre.replace(
                        "Reverso ",
                        "Retención ",
                    ),
                    "activo",
                )

                lineas.append(
                    {
                        "cuenta_id": cuenta_ret.id,
                        "debito": 0,
                        "credito": valor,
                        "descripcion": nombre,
                        "orden": orden,
                    },
                )

                orden += 1

            total_debito = 0.0
            total_credito = 0.0

            for linea in lineas:

                db.add(
                    AsientoDetalle(
                        asiento_id=asiento.id,
                        **linea,
                    ),
                )

                total_debito += float(
                    linea["debito"],
                )

                total_credito += float(
                    linea["credito"],
                )

            asiento.total_debito = total_debito
            asiento.total_credito = total_credito

            db.commit()
            db.refresh(asiento)

            return asiento

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def registrar_nota_credito_compra(
        cls,
        nota,
    ) -> AsientoContable:

        cls.inicializar_plan()

        db = SessionLocal()

        try:

            cuenta_iva = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "iva_descontable",
                    "240801",
                ),
                "IVA descontable",
                "activo",
            )

            cuenta_cxp = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "cuentas_por_pagar",
                    "220501",
                ),
                "Proveedores nacionales",
                "pasivo",
            )

            from aplicacion.modulos.contabilidad.reglas.servicio_reglas import (
                ServicioReglasContabilizacion,
            )

            bases_por_cuenta: dict[str, float] = {}

            for detalle in nota.detalles:

                monto = float(
                    detalle.total_linea or 0,
                )

                producto = None

                if detalle.producto_id:

                    producto = (
                        db.query(Producto)
                        .filter(
                            Producto.id
                            == detalle.producto_id,
                        )
                        .first()
                    )

                cuentas = (
                    ServicioReglasContabilizacion
                    .resolver_cuentas_compra(
                        producto_tipo=(
                            producto.tipo
                            if producto
                            else None
                        ),
                        tiene_producto=bool(
                            detalle.producto_id,
                        ),
                    )
                )

                codigo_credito = cuentas["debito"]

                bases_por_cuenta[codigo_credito] = (
                    bases_por_cuenta.get(
                        codigo_credito,
                        0.0,
                    )
                    + monto
                )

            iva = float(
                nota.iva or 0,
            )

            total = float(
                nota.total or 0,
            )

            asiento = AsientoContable(
                numero=cls._siguiente_numero(
                    db,
                ),
                fecha=nota.fecha or date.today(),
                descripcion=(
                    f"Nota crédito compra "
                    f"{nota.numero}"
                ),
                origen="nota_credito_compra",
                origen_id=nota.id,
            )

            db.add(asiento)
            db.flush()

            lineas: list[dict] = []
            orden = 0

            if total > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_cxp.id,
                        "debito": total,
                        "credito": 0,
                        "descripcion": "Reducción CxP",
                        "orden": orden,
                    },
                )

                orden += 1

            for codigo_cuenta, monto in bases_por_cuenta.items():

                if monto <= 0:

                    continue

                cuenta = cls._obtener_o_crear_cuenta(
                    db,
                    codigo_cuenta,
                    "Reverso compra",
                    "activo",
                )

                lineas.append(
                    {
                        "cuenta_id": cuenta.id,
                        "debito": 0,
                        "credito": monto,
                        "descripcion": "Reverso compra",
                        "orden": orden,
                    },
                )

                orden += 1

            if iva > 0:

                lineas.append(
                    {
                        "cuenta_id": cuenta_iva.id,
                        "debito": 0,
                        "credito": iva,
                        "descripcion": "Reverso IVA descontable",
                        "orden": orden,
                    },
                )

            total_debito = 0.0
            total_credito = 0.0

            for linea in lineas:

                db.add(
                    AsientoDetalle(
                        asiento_id=asiento.id,
                        cuenta_id=linea["cuenta_id"],
                        debito=linea["debito"],
                        credito=linea["credito"],
                        descripcion=linea[
                            "descripcion"
                        ],
                        orden=linea["orden"],
                    ),
                )

                total_debito += float(
                    linea["debito"] or 0,
                )

                total_credito += float(
                    linea["credito"] or 0,
                )

            asiento.total_debito = total_debito
            asiento.total_credito = total_credito

            db.commit()
            db.refresh(asiento)

            return asiento

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def registrar_nota_debito_venta(
        cls,
        nota,
    ) -> AsientoContable:

        asiento = cls.registrar_factura_venta(
            nota,
        )

        db = SessionLocal()

        try:

            registro = (
                db.query(AsientoContable)
                .filter(
                    AsientoContable.id == asiento.id,
                )
                .first()
            )

            if registro is not None:

                registro.origen = "nota_debito_venta"
                registro.origen_id = nota.id
                registro.descripcion = (
                    f"Nota débito venta "
                    f"{nota.numero}"
                )

                db.commit()
                db.refresh(registro)

                return registro

            return asiento

        finally:

            db.close()

    @classmethod
    def registrar_liquidacion_nomina(
        cls,
        periodo,
        totales: dict[str, float],
    ) -> AsientoContable:

        cls.inicializar_plan()

        db = SessionLocal()

        try:

            cuenta_gasto = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "gasto_nomina",
                    "510506",
                ),
                "Gastos de personal",
                "gasto",
            )

            cuenta_por_pagar = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "nomina_por_pagar",
                    "250501",
                ),
                "Nómina por pagar",
                "pasivo",
            )

            cuenta_seguridad = cls._obtener_o_crear_cuenta(
                db,
                cls._cuenta(
                    "seguridad_social_por_pagar",
                    "237005",
                ),
                "Seguridad social por pagar",
                "pasivo",
            )

            devengado = float(
                totales.get(
                    "devengado",
                    0,
                )
                or 0,
            )

            deducciones = float(
                totales.get(
                    "deducciones",
                    0,
                )
                or 0,
            )

            neto = float(
                totales.get(
                    "neto",
                    0,
                )
                or 0,
            )

            aportes = float(
                totales.get(
                    "aportes",
                    0,
                )
                or 0,
            )

            total_gasto = devengado + aportes
            total_seguridad = deducciones + aportes

            asiento = AsientoContable(
                numero=cls._siguiente_numero(
                    db,
                ),
                fecha=date.today(),
                descripcion=(
                    "Liquidación nómina "
                    f"{periodo.mes:02d}/"
                    f"{periodo.anio}"
                ),
                origen="nomina",
                origen_id=periodo.id,
            )

            db.add(asiento)
            db.flush()

            lineas = [
                {
                    "cuenta_id": cuenta_gasto.id,
                    "debito": total_gasto,
                    "credito": 0,
                    "descripcion": "Gasto de nómina",
                    "orden": 0,
                },
                {
                    "cuenta_id": cuenta_por_pagar.id,
                    "debito": 0,
                    "credito": neto,
                    "descripcion": "Neto por pagar",
                    "orden": 1,
                },
                {
                    "cuenta_id": cuenta_seguridad.id,
                    "debito": 0,
                    "credito": total_seguridad,
                    "descripcion": "Aportes y deducciones SS",
                    "orden": 2,
                },
            ]

            total_debito = 0.0
            total_credito = 0.0

            for linea in lineas:

                db.add(
                    AsientoDetalle(
                        asiento_id=asiento.id,
                        **linea,
                    ),
                )

                total_debito += float(
                    linea["debito"],
                )

                total_credito += float(
                    linea["credito"],
                )

            asiento.total_debito = total_debito
            asiento.total_credito = total_credito

            db.commit()
            db.refresh(asiento)

            return asiento

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
