from __future__ import annotations

from datetime import date

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.productos.modelos import (
    Producto,
    ProductoVariante,
)
from aplicacion.maestros.productos.servicios import (
    ServicioProducto,
)
from aplicacion.nucleo.configuracion import Configuracion

from sqlalchemy import func

from .modelos import (
    Bodega,
    ExistenciaBodega,
    MovimientoInventario,
)


class ServicioInventario:

    @classmethod
    def _codigo_bodega(cls) -> str:

        return str(
            Configuracion.obtener(
                "inventario",
                "bodega_predeterminada",
            )
            or "PRINCIPAL",
        )

    @classmethod
    def inicializar_bodega(cls) -> Bodega:

        db = SessionLocal()

        try:

            codigo = cls._codigo_bodega()

            bodega = (
                db.query(Bodega)
                .filter(
                    Bodega.codigo == codigo,
                )
                .first()
            )

            if bodega is not None:

                return bodega

            bodega = Bodega(
                codigo=codigo,
                nombre="Bodega principal",
                activo=True,
            )

            db.add(bodega)
            db.commit()
            db.refresh(bodega)

            return bodega

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def _resolver_bodega(
        cls,
        db,
        bodega_id: int | None = None,
    ) -> Bodega:

        if bodega_id is not None:

            bodega = (
                db.query(Bodega)
                .filter(
                    Bodega.id == bodega_id,
                )
                .first()
            )

            if bodega is not None:

                return bodega

        codigo = cls._codigo_bodega()

        bodega = (
            db.query(Bodega)
            .filter(
                Bodega.codigo == codigo,
            )
            .first()
        )

        if bodega is None:

            bodega = Bodega(
                codigo=codigo,
                nombre="Bodega principal",
                activo=True,
            )

            db.add(bodega)
            db.flush()

        return bodega

    @classmethod
    def _bodega_operacion(
        cls,
        db,
        *,
        bodega_id: int | None = None,
        contexto: str = "ventas",
    ) -> Bodega:

        if bodega_id is not None:

            return cls._resolver_bodega(
                db,
                bodega_id,
            )

        clave_config = (
            "bodega_id"
            if contexto == "pos"
            else "bodega_ventas_id"
        )

        seccion = (
            "pos"
            if contexto == "pos"
            else "inventario"
        )

        valor = Configuracion.obtener(
            seccion,
            clave_config,
        )

        if valor not in (
            None,
            "",
            0,
            "0",
        ):

            try:

                return cls._resolver_bodega(
                    db,
                    int(valor),
                )

            except (
                TypeError,
                ValueError,
            ):

                pass

        return cls._resolver_bodega(
            db,
            None,
        )

    @classmethod
    def _buscar_existencia_bodega(
        cls,
        db,
        *,
        bodega_id: int,
        producto_id: int,
        producto_variante_id: int | None,
    ) -> ExistenciaBodega | None:

        consulta = (
            db.query(
                ExistenciaBodega,
            )
            .filter(
                ExistenciaBodega.bodega_id
                == bodega_id,
                ExistenciaBodega.producto_id
                == producto_id,
            )
        )

        if producto_variante_id:

            consulta = consulta.filter(
                ExistenciaBodega.producto_variante_id
                == producto_variante_id,
            )

        else:

            consulta = consulta.filter(
                ExistenciaBodega.producto_variante_id.is_(
                    None,
                ),
            )

        return consulta.first()

    @classmethod
    def _disponible_bodega(
        cls,
        db,
        *,
        bodega_id: int,
        producto_id: int,
        producto_variante_id: int | None,
    ) -> float:

        registro = cls._buscar_existencia_bodega(
            db,
            bodega_id=bodega_id,
            producto_id=producto_id,
            producto_variante_id=(
                producto_variante_id
            ),
        )

        if registro is None:

            return 0.0

        return max(
            0.0,
            float(
                registro.cantidad or 0,
            )
            - float(
                registro.cantidad_reservada
                or 0,
            ),
        )

    @classmethod
    def _obtener_existencia(
        cls,
        db,
        producto: Producto,
        variante_id: int | None,
        bodega_id: int | None = None,
    ) -> tuple[float, ProductoVariante | None]:

        if bodega_id is not None:

            bodega = cls._resolver_bodega(
                db,
                bodega_id,
            )

            if variante_id:

                variante = (
                    db.query(
                        ProductoVariante,
                    )
                    .filter(
                        ProductoVariante.id
                        == variante_id,
                    )
                    .first()
                )

                if variante is None:

                    raise ValueError(
                        "La variante del producto no existe.",
                    )

                registro = cls._buscar_existencia_bodega(
                    db,
                    bodega_id=bodega.id,
                    producto_id=producto.id,
                    producto_variante_id=variante_id,
                )

                return (
                    float(
                        registro.cantidad
                        if registro
                        else 0,
                    ),
                    variante,
                )

            registro = cls._buscar_existencia_bodega(
                db,
                bodega_id=bodega.id,
                producto_id=producto.id,
                producto_variante_id=None,
            )

            return (
                float(
                    registro.cantidad
                    if registro
                    else 0,
                ),
                None,
            )

        if variante_id:

            variante = (
                db.query(ProductoVariante)
                .filter(
                    ProductoVariante.id
                    == variante_id,
                )
                .first()
            )

            if variante is None:

                raise ValueError(
                    "La variante del producto no existe.",
                )

            return (
                float(
                    variante.existencia or 0,
                ),
                variante,
            )

        return (
            float(
                getattr(
                    producto,
                    "existencia",
                    0,
                )
                or 0,
            ),
            None,
        )

    @classmethod
    def _sincronizar_existencia_global(
        cls,
        db,
        producto_id: int,
        producto_variante_id: int | None = None,
    ) -> None:

        if producto_variante_id:

            total = (
                db.query(
                    func.coalesce(
                        func.sum(
                            ExistenciaBodega.cantidad,
                        ),
                        0,
                    ),
                )
                .filter(
                    ExistenciaBodega.producto_variante_id
                    == producto_variante_id,
                )
                .scalar()
            )

            variante = (
                db.query(
                    ProductoVariante,
                )
                .filter(
                    ProductoVariante.id
                    == producto_variante_id,
                )
                .first()
            )

            if variante is not None:

                variante.existencia = float(
                    total or 0,
                )

            cls._sincronizar_variantes(
                db,
                producto_id,
            )

            return

        total = (
            db.query(
                func.coalesce(
                    func.sum(
                        ExistenciaBodega.cantidad,
                    ),
                    0,
                ),
            )
            .filter(
                ExistenciaBodega.producto_id
                == producto_id,
                ExistenciaBodega.producto_variante_id.is_(
                    None,
                ),
            )
            .scalar()
        )

        producto = (
            db.query(
                Producto,
            )
            .filter(
                Producto.id == producto_id,
            )
            .first()
        )

        if producto is not None:

            producto.existencia = float(
                total or 0,
            )

    @classmethod
    def _actualizar_existencia_bodega(
        cls,
        db,
        *,
        bodega_id: int,
        producto: Producto,
        variante: ProductoVariante | None,
        cantidad: float,
        sumar: bool,
    ) -> None:

        variante_id = (
            variante.id
            if variante is not None
            else None
        )

        registro = cls._buscar_existencia_bodega(
            db,
            bodega_id=bodega_id,
            producto_id=producto.id,
            producto_variante_id=variante_id,
        )

        if registro is None:

            if not sumar:

                raise ValueError(
                    "Stock insuficiente "
                    "(disponible 0).",
                )

            registro = ExistenciaBodega(
                bodega_id=bodega_id,
                producto_id=producto.id,
                producto_variante_id=variante_id,
                cantidad=0,
            )

            db.add(
                registro,
            )

            db.flush()

        existencia = float(
            registro.cantidad or 0,
        )

        if sumar:

            registro.cantidad = (
                existencia + cantidad
            )

        else:

            if existencia < cantidad:

                raise ValueError(
                    f"Stock insuficiente "
                    f"(disponible {existencia:g}).",
                )

            registro.cantidad = (
                existencia - cantidad
            )

        cls._sincronizar_existencia_global(
            db,
            producto.id,
            variante_id,
        )

    @classmethod
    def _actualizar_existencia(
        cls,
        db,
        producto: Producto,
        variante: ProductoVariante | None,
        cantidad: float,
        *,
        sumar: bool,
        bodega_id: int,
    ) -> None:

        cls._actualizar_existencia_bodega(
            db,
            bodega_id=bodega_id,
            producto=producto,
            variante=variante,
            cantidad=cantidad,
            sumar=sumar,
        )

    @classmethod
    def sembrar_existencias_desde_productos(
        cls,
    ) -> None:

        db = SessionLocal()

        try:

            if (
                db.query(
                    ExistenciaBodega.id,
                ).first()
                is not None
            ):

                return

            bodega = cls._resolver_bodega(
                db,
                None,
            )

            productos = (
                db.query(
                    Producto,
                )
                .filter(
                    Producto.tipo != "servicio",
                )
                .all()
            )

            for producto in productos:

                if producto.maneja_variantes:

                    variantes = (
                        db.query(
                            ProductoVariante,
                        )
                        .filter(
                            ProductoVariante.producto_id
                            == producto.id,
                            ProductoVariante.activo.is_(
                                True,
                            ),
                        )
                        .all()
                    )

                    for variante in variantes:

                        cantidad = float(
                            variante.existencia
                            or 0,
                        )

                        if cantidad <= 0:

                            continue

                        db.add(
                            ExistenciaBodega(
                                bodega_id=bodega.id,
                                producto_id=producto.id,
                                producto_variante_id=variante.id,
                                cantidad=cantidad,
                            ),
                        )

                    continue

                cantidad = float(
                    getattr(
                        producto,
                        "existencia",
                        0,
                    )
                    or 0,
                )

                if cantidad <= 0:

                    continue

                db.add(
                    ExistenciaBodega(
                        bodega_id=bodega.id,
                        producto_id=producto.id,
                        producto_variante_id=None,
                        cantidad=cantidad,
                    ),
                )

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def registrar_entrada(
        cls,
        db,
        *,
        bodega_id: int,
        producto: Producto,
        producto_variante_id: int | None,
        cantidad: float,
        costo_unitario: float,
        referencia: str,
        referencia_id: int,
        fecha: date,
        observaciones: str = "",
    ) -> MovimientoInventario:

        cantidad = float(
            cantidad or 0,
        )

        if cantidad <= 0:

            raise ValueError(
                "La cantidad debe ser mayor a cero.",
            )

        _, variante = cls._obtener_existencia(
            db,
            producto,
            producto_variante_id,
            bodega_id=bodega_id,
        )

        costo = float(
            costo_unitario
            or producto.costo
            or 0,
        )

        movimiento = MovimientoInventario(
            bodega_id=bodega_id,
            producto_id=producto.id,
            producto_variante_id=producto_variante_id,
            tipo="entrada",
            cantidad=cantidad,
            costo_unitario=costo,
            referencia=referencia,
            referencia_id=referencia_id,
            fecha=fecha,
            observaciones=observaciones,
        )

        db.add(
            movimiento,
        )

        cls._actualizar_existencia_bodega(
            db,
            bodega_id=bodega_id,
            producto=producto,
            variante=variante,
            cantidad=cantidad,
            sumar=True,
        )

        if costo > 0:

            if variante is not None:

                variante.costo = costo

            else:

                producto.costo = costo

        return movimiento

    @classmethod
    def _sincronizar_variantes(
        cls,
        db,
        producto_id: int,
    ) -> None:

        from aplicacion.maestros.productos.repositorio import (
            RepositorioProducto,
        )

        producto = (
            db.query(Producto)
            .filter(
                Producto.id == producto_id,
            )
            .first()
        )

        if (
            producto is not None
            and producto.maneja_variantes
        ):

            RepositorioProducto.sincronizar_existencia_producto(
                producto.id,
            )

    @classmethod
    def _movimientos_existen(
        cls,
        db,
        referencia: str,
        referencia_id: int,
    ) -> bool:

        return (
            db.query(
                MovimientoInventario.id,
            )
            .filter(
                MovimientoInventario.referencia
                == referencia,
                MovimientoInventario.referencia_id
                == referencia_id,
            )
            .first()
            is not None
        )

    @classmethod
    def _remision_vinculada(
        cls,
        db,
        factura,
    ):

        from aplicacion.modulos.ventas.remisiones.modelos import (
            RemisionVenta,
        )

        if factura.cotizacion_id:

            return (
                db.query(
                    RemisionVenta,
                )
                .filter(
                    RemisionVenta.cotizacion_id
                    == factura.cotizacion_id,
                )
                .first()
            )

        if factura.pedido_id:

            return (
                db.query(
                    RemisionVenta,
                )
                .filter(
                    RemisionVenta.pedido_id
                    == factura.pedido_id,
                )
                .first()
            )

        return None

    @classmethod
    def _marcar_inventario_factura(
        cls,
        db,
        factura_id: int,
    ) -> None:

        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        registro = (
            db.query(
                FacturaVenta,
            )
            .filter(
                FacturaVenta.id == factura_id,
            )
            .first()
        )

        if registro is not None:

            registro.inventario_aplicado = True

    @classmethod
    def _marcar_inventario_nota_credito(
        cls,
        db,
        nota_id: int,
    ) -> None:

        from aplicacion.modulos.ventas.notas_credito.modelos import (
            NotaCreditoVenta,
        )

        registro = (
            db.query(
                NotaCreditoVenta,
            )
            .filter(
                NotaCreditoVenta.id == nota_id,
            )
            .first()
        )

        if registro is not None:

            registro.inventario_aplicado = True

    @classmethod
    def consultar_kardex(
        cls,
        *,
        bodega_id: int | None = None,
        producto_id: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[dict]:

        db = SessionLocal()

        try:

            consulta = db.query(
                MovimientoInventario,
            )

            if bodega_id is not None:

                consulta = consulta.filter(
                    MovimientoInventario.bodega_id
                    == bodega_id,
                )

            if producto_id is not None:

                consulta = consulta.filter(
                    MovimientoInventario.producto_id
                    == producto_id,
                )

            if fecha_desde is not None:

                consulta = consulta.filter(
                    MovimientoInventario.fecha
                    >= fecha_desde,
                )

            if fecha_hasta is not None:

                consulta = consulta.filter(
                    MovimientoInventario.fecha
                    <= fecha_hasta,
                )

            movimientos = consulta.order_by(
                MovimientoInventario.fecha,
                MovimientoInventario.id,
            ).all()

            if not movimientos:

                return []

            producto_ids = {
                movimiento.producto_id
                for movimiento in movimientos
                if movimiento.producto_id
            }

            variante_ids = {
                movimiento.producto_variante_id
                for movimiento in movimientos
                if movimiento.producto_variante_id
            }

            bodega_ids = {
                movimiento.bodega_id
                for movimiento in movimientos
            }

            productos = {

                producto.id: producto

                for producto in (
                    db.query(Producto)
                    .filter(
                        Producto.id.in_(
                            producto_ids,
                        ),
                    )
                    .all()
                )

            } if producto_ids else {}

            variantes = {

                variante.id: variante

                for variante in (
                    db.query(ProductoVariante)
                    .filter(
                        ProductoVariante.id.in_(
                            variante_ids,
                        ),
                    )
                    .all()
                )

            } if variante_ids else {}

            bodegas = {

                bodega.id: bodega

                for bodega in (
                    db.query(Bodega)
                    .filter(
                        Bodega.id.in_(
                            bodega_ids,
                        ),
                    )
                    .all()
                )

            }

            saldos: dict[
                tuple,
                float,
            ] = {}
            filas: list[dict] = []

            for movimiento in movimientos:

                cantidad = float(
                    movimiento.cantidad or 0,
                )

                clave = (
                    movimiento.bodega_id,
                    movimiento.producto_id,
                    movimiento.producto_variante_id,
                )

                saldo = saldos.get(
                    clave,
                    0.0,
                )

                if movimiento.tipo == "salida":

                    saldo -= cantidad

                else:

                    saldo += cantidad

                saldos[clave] = saldo

                producto = productos.get(
                    movimiento.producto_id,
                )

                variante = variantes.get(
                    movimiento.producto_variante_id,
                )

                bodega = bodegas.get(
                    movimiento.bodega_id,
                )

                if variante is not None:

                    codigo = str(
                        variante.codigo or "",
                    )

                    variante_texto = (
                        ServicioProducto._etiqueta_variante(
                            variante,
                            incluir_stock=False,
                        )
                    )

                else:

                    codigo = str(
                        producto.codigo or "",
                    ) if producto else ""

                    variante_texto = ""

                filas.append(
                    {
                        "fecha": movimiento.fecha,
                        "bodega": (
                            f"{bodega.codigo} - {bodega.nombre}"
                            if bodega
                            else ""
                        ),
                        "codigo": codigo,
                        "producto": (
                            producto.nombre
                            if producto
                            else ""
                        ),
                        "variante": variante_texto,
                        "tipo": movimiento.tipo,
                        "cantidad": cantidad,
                        "costo_unitario": float(
                            movimiento.costo_unitario
                            or 0,
                        ),
                        "referencia": (
                            movimiento.referencia
                            or ""
                        ),
                        "observaciones": (
                            movimiento.observaciones
                            or ""
                        ),
                        "saldo": saldo,
                    },
                )

            return filas

        finally:

            db.close()

    @classmethod
    def registrar_ajuste(
        cls,
        *,
        bodega_id: int,
        producto_id: int,
        tipo: str,
        cantidad: float,
        costo_unitario: float = 0,
        fecha: date | None = None,
        observaciones: str = "",
        producto_variante_id: int | None = None,
    ) -> MovimientoInventario:

        tipo = tipo.strip().lower()

        if tipo not in (
            "entrada",
            "salida",
        ):

            raise ValueError(
                "El tipo debe ser entrada o salida.",
            )

        cantidad = float(cantidad or 0)

        if cantidad <= 0:

            raise ValueError(
                "La cantidad debe ser mayor a cero.",
            )

        db = SessionLocal()

        try:

            producto = (
                db.query(Producto)
                .filter(
                    Producto.id == producto_id,
                )
                .first()
            )

            if producto is None:

                raise ValueError(
                    "Producto no encontrado.",
                )

            if producto.tipo == "servicio":

                raise ValueError(
                    "No se ajusta inventario de servicios.",
                )

            existencia_actual, variante = (
                cls._obtener_existencia(
                    db,
                    producto,
                    producto_variante_id,
                    bodega_id=bodega_id,
                )
            )

            if (
                tipo == "salida"
                and existencia_actual < cantidad
            ):

                raise ValueError(
                    f"Stock insuficiente "
                    f"(disponible {existencia_actual:g}).",
                )

            costo = float(
                costo_unitario
                or producto.costo
                or 0,
            )

            movimiento = MovimientoInventario(
                bodega_id=bodega_id,
                producto_id=producto_id,
                producto_variante_id=producto_variante_id,
                tipo=tipo,
                cantidad=cantidad,
                costo_unitario=costo,
                referencia="ajuste",
                referencia_id=None,
                fecha=fecha or date.today(),
                observaciones=observaciones.strip(),
            )

            db.add(movimiento)

            cls._actualizar_existencia(
                db,
                producto,
                variante,
                cantidad,
                sumar=(tipo == "entrada"),
                bodega_id=bodega_id,
            )

            db.commit()
            db.refresh(movimiento)

            cls._sincronizar_variantes(
                db,
                producto_id,
            )

            return movimiento

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def registrar_traslado(
        cls,
        *,
        bodega_origen_id: int,
        bodega_destino_id: int,
        producto_id: int,
        cantidad: float,
        fecha: date | None = None,
        observaciones: str = "",
        producto_variante_id: int | None = None,
    ) -> tuple[
        MovimientoInventario,
        MovimientoInventario,
    ]:

        if bodega_origen_id == bodega_destino_id:

            raise ValueError(
                "La bodega origen y destino deben ser diferentes.",
            )

        cantidad = float(cantidad or 0)

        if cantidad <= 0:

            raise ValueError(
                "La cantidad debe ser mayor a cero.",
            )

        db = SessionLocal()

        try:

            producto = (
                db.query(Producto)
                .filter(
                    Producto.id == producto_id,
                )
                .first()
            )

            if producto is None:

                raise ValueError(
                    "Producto no encontrado.",
                )

            if producto.tipo == "servicio":

                raise ValueError(
                    "No se trasladan servicios.",
                )

            existencia_actual, variante = (
                cls._obtener_existencia(
                    db,
                    producto,
                    producto_variante_id,
                    bodega_id=bodega_origen_id,
                )
            )

            if existencia_actual < cantidad:

                raise ValueError(
                    f"Stock insuficiente en bodega origen "
                    f"(disponible {existencia_actual:g}).",
                )

            costo = float(
                producto.costo or 0,
            )

            fecha_mov = fecha or date.today()
            obs = observaciones.strip()

            salida = MovimientoInventario(
                bodega_id=bodega_origen_id,
                producto_id=producto_id,
                producto_variante_id=producto_variante_id,
                tipo="salida",
                cantidad=cantidad,
                costo_unitario=costo,
                referencia="traslado",
                referencia_id=bodega_destino_id,
                fecha=fecha_mov,
                observaciones=obs,
            )

            entrada = MovimientoInventario(
                bodega_id=bodega_destino_id,
                producto_id=producto_id,
                producto_variante_id=producto_variante_id,
                tipo="entrada",
                cantidad=cantidad,
                costo_unitario=costo,
                referencia="traslado",
                referencia_id=bodega_origen_id,
                fecha=fecha_mov,
                observaciones=obs,
            )

            db.add(salida)
            db.add(entrada)

            cls._actualizar_existencia_bodega(
                db,
                bodega_id=bodega_origen_id,
                producto=producto,
                variante=variante,
                cantidad=cantidad,
                sumar=False,
            )

            cls._actualizar_existencia_bodega(
                db,
                bodega_id=bodega_destino_id,
                producto=producto,
                variante=variante,
                cantidad=cantidad,
                sumar=True,
            )

            # Traslado: existencia global (suma bodegas) no cambia.

            db.commit()
            db.refresh(salida)
            db.refresh(entrada)

            cls._sincronizar_variantes(
                db,
                producto_id,
            )

            return salida, entrada

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def registrar_entrada_factura_compra(
        cls,
        factura,
    ) -> list[MovimientoInventario]:

        from aplicacion.modulos.compras.integracion_oc import (
            ServicioIntegracionCompras,
        )

        db = SessionLocal()

        try:

            bodega = cls._resolver_bodega(
                db,
                None,
            )

            movimientos: list[
                MovimientoInventario
            ] = []

            for detalle in factura.detalles:

                if ServicioIntegracionCompras.omitir_inventario_linea(
                    db,
                    factura,
                    detalle,
                ):

                    continue

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

                if producto is None:

                    continue

                if producto.tipo == "servicio":

                    continue

                cantidad = float(
                    detalle.cantidad or 0,
                )

                if cantidad <= 0:

                    continue

                variante_id = getattr(
                    detalle,
                    "producto_variante_id",
                    None,
                )

                movimiento = cls.registrar_entrada(
                    db,
                    bodega_id=bodega.id,
                    producto=producto,
                    producto_variante_id=variante_id,
                    cantidad=cantidad,
                    costo_unitario=float(
                        detalle.precio_unitario
                        or 0,
                    ),
                    referencia="factura_compra",
                    referencia_id=factura.id,
                    fecha=factura.fecha
                    or date.today(),
                    observaciones=(
                        f"FC {factura.numero}"
                    ),
                )

                movimientos.append(
                    movimiento,
                )

            db.commit()

            for movimiento in movimientos:

                db.refresh(movimiento)

            return movimientos

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def registrar_salida_remision(
        cls,
        remision,
        *,
        db=None,
    ) -> list[MovimientoInventario]:

        if getattr(
            remision,
            "inventario_aplicado",
            False,
        ):

            return []

        return cls._registrar_salida(
            remision,
            referencia="remision_venta",
            etiqueta="REM",
            db=db,
        )

    @classmethod
    def registrar_salida_factura_venta(
        cls,
        factura,
        *,
        db=None,
    ) -> list[MovimientoInventario]:

        propia_sesion = db is None

        if propia_sesion:

            db = SessionLocal()

        try:

            if getattr(
                factura,
                "inventario_aplicado",
                False,
            ):

                return []

            if cls._movimientos_existen(
                db,
                "factura_venta",
                factura.id,
            ):

                cls._marcar_inventario_factura(
                    db,
                    factura.id,
                )

                if propia_sesion:

                    db.commit()

                return []

            remision = cls._remision_vinculada(
                db,
                factura,
            )

            if (
                remision is not None
                and remision.inventario_aplicado
            ):

                cls._marcar_inventario_factura(
                    db,
                    factura.id,
                )

                if propia_sesion:

                    db.commit()

                return []

            movimientos = cls._registrar_salida(
                factura,
                referencia="factura_venta",
                etiqueta="FV",
                db=db,
            )

            cls._marcar_inventario_factura(
                db,
                factura.id,
            )

            if propia_sesion:

                db.commit()

            return movimientos

        except Exception:

            if propia_sesion:

                db.rollback()

            raise

        finally:

            if propia_sesion:

                db.close()

    @classmethod
    def registrar_entrada_nota_credito_venta(
        cls,
        nota,
        *,
        db=None,
    ) -> list[MovimientoInventario]:

        if getattr(
            nota,
            "inventario_aplicado",
            False,
        ):

            return []

        propia_sesion = db is None

        if propia_sesion:

            db = SessionLocal()

        try:

            if cls._movimientos_existen(
                db,
                "nota_credito_venta",
                nota.id,
            ):

                cls._marcar_inventario_nota_credito(
                    db,
                    nota.id,
                )

                if propia_sesion:

                    db.commit()

                return []

            bodega = cls._bodega_operacion(
                db,
                contexto="ventas",
            )

            movimientos: list[
                MovimientoInventario
            ] = []

            for detalle in nota.detalles:

                if not detalle.producto_id:

                    continue

                producto = (
                    db.query(
                        Producto,
                    )
                    .filter(
                        Producto.id
                        == detalle.producto_id,
                    )
                    .first()
                )

                if producto is None:

                    continue

                if producto.tipo == "servicio":

                    continue

                cantidad = float(
                    detalle.cantidad or 0,
                )

                if cantidad <= 0:

                    continue

                variante_id = getattr(
                    detalle,
                    "producto_variante_id",
                    None,
                )

                movimiento = cls.registrar_entrada(
                    db,
                    bodega_id=bodega.id,
                    producto=producto,
                    producto_variante_id=variante_id,
                    cantidad=cantidad,
                    costo_unitario=float(
                        producto.costo or 0,
                    ),
                    referencia="nota_credito_venta",
                    referencia_id=nota.id,
                    fecha=nota.fecha
                    or date.today(),
                    observaciones=(
                        f"NC {nota.numero}"
                    ),
                )

                movimientos.append(
                    movimiento,
                )

            cls._marcar_inventario_nota_credito(
                db,
                nota.id,
            )

            if propia_sesion:

                db.commit()

                for movimiento in movimientos:

                    db.refresh(
                        movimiento,
                    )

            producto_ids = {
                detalle.producto_id
                for detalle in nota.detalles
                if detalle.producto_id
            }

            for producto_id in producto_ids:

                cls._sincronizar_variantes(
                    db,
                    producto_id,
                )

            return movimientos

        except Exception:

            if propia_sesion:

                db.rollback()

            raise

        finally:

            if propia_sesion:

                db.close()

    @classmethod
    def _registrar_salida(
        cls,
        documento,
        *,
        referencia: str,
        etiqueta: str,
        db=None,
    ) -> list[MovimientoInventario]:

        propia_sesion = db is None

        if propia_sesion:

            db = SessionLocal()

        try:

            if cls._movimientos_existen(
                db,
                referencia,
                documento.id,
            ):

                return []

            bodega = cls._bodega_operacion(
                db,
                contexto="ventas",
            )

            movimientos: list[
                MovimientoInventario
            ] = []

            for detalle in documento.detalles:

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

                if producto is None:

                    continue

                if producto.tipo == "servicio":

                    continue

                cantidad = float(
                    detalle.cantidad or 0,
                )

                if cantidad <= 0:

                    continue

                variante_id = getattr(
                    detalle,
                    "producto_variante_id",
                    None,
                )

                existencia_actual, variante = (
                    cls._obtener_existencia(
                        db,
                        producto,
                        variante_id,
                        bodega_id=bodega.id,
                    )
                )

                disponible = cls._disponible_bodega(
                    db,
                    bodega_id=bodega.id,
                    producto_id=producto.id,
                    producto_variante_id=variante_id,
                )

                if disponible < cantidad:

                    raise ValueError(
                        f"Stock insuficiente para "
                        f"{detalle.descripcion} "
                        f"en {bodega.codigo} "
                        f"(disponible "
                        f"{disponible:g}).",
                    )

                pedido_id = getattr(
                    documento,
                    "pedido_id",
                    None,
                )

                if pedido_id:

                    from aplicacion.modulos.ventas.pedidos.reservas import (
                        ServicioReservaPedido,
                    )

                    ServicioReservaPedido.consumir_por_salida(
                        db,
                        pedido_id=pedido_id,
                        producto_id=producto.id,
                        producto_variante_id=variante_id,
                        bodega_id=bodega.id,
                        cantidad=cantidad,
                    )

                costo = float(
                    producto.costo or 0,
                )

                movimiento = MovimientoInventario(
                    bodega_id=bodega.id,
                    producto_id=producto.id,
                    producto_variante_id=variante_id,
                    tipo="salida",
                    cantidad=cantidad,
                    costo_unitario=costo,
                    referencia=referencia,
                    referencia_id=documento.id,
                    fecha=documento.fecha or date.today(),
                    observaciones=(
                        f"{etiqueta} "
                        f"{documento.numero}"
                    ),
                )

                db.add(movimiento)
                movimientos.append(movimiento)

                cls._actualizar_existencia_bodega(
                    db,
                    bodega_id=bodega.id,
                    producto=producto,
                    variante=variante,
                    cantidad=cantidad,
                    sumar=False,
                )

            if propia_sesion:

                db.commit()

                for movimiento in movimientos:

                    db.refresh(
                        movimiento,
                    )

            from aplicacion.maestros.productos.repositorio import (
                RepositorioProducto,
            )

            producto_ids = {
                detalle.producto_id
                for detalle in documento.detalles
                if detalle.producto_id
            }

            for producto_id in producto_ids:

                producto = (
                    db.query(
                        Producto,
                    )
                    .filter(
                        Producto.id
                        == producto_id,
                    )
                    .first()
                )

                if (
                    producto is not None
                    and producto.maneja_variantes
                ):

                    RepositorioProducto.sincronizar_existencia_producto(
                        producto.id,
                    )

            return movimientos

        except Exception:

            if propia_sesion:

                db.rollback()

            raise

        finally:

            if propia_sesion:

                db.close()

    @classmethod
    def revertir_recepcion_compra(
        cls,
        recepcion,
        *,
        db=None,
    ) -> list[MovimientoInventario]:

        propia_sesion = db is None

        if propia_sesion:

            db = SessionLocal()

        try:

            if cls._movimientos_existen(
                db,
                "anulacion_recepcion",
                recepcion.id,
            ):

                return []

            movimientos: list[
                MovimientoInventario
            ] = []

            for detalle in recepcion.detalles:

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

                variante_id = (
                    detalle.producto_variante_id
                )

                existencia_actual, variante = (
                    cls._obtener_existencia(
                        db,
                        producto,
                        variante_id,
                        bodega_id=recepcion.bodega_id,
                    )
                )

                if existencia_actual < cantidad:

                    raise ValueError(
                        f"Stock insuficiente para anular "
                        f"recepción en "
                        f"{detalle.descripcion}.",
                    )

                costo = float(
                    detalle.costo_unitario
                    or producto.costo
                    or 0,
                )

                movimiento = MovimientoInventario(
                    bodega_id=recepcion.bodega_id,
                    producto_id=producto.id,
                    producto_variante_id=variante_id,
                    tipo="salida",
                    cantidad=cantidad,
                    costo_unitario=costo,
                    referencia="anulacion_recepcion",
                    referencia_id=recepcion.id,
                    fecha=recepcion.fecha,
                    observaciones=(
                        f"Anulación REC "
                        f"{recepcion.numero}"
                    ),
                )

                db.add(movimiento)
                movimientos.append(movimiento)

                cls._actualizar_existencia_bodega(
                    db,
                    bodega_id=recepcion.bodega_id,
                    producto=producto,
                    variante=variante,
                    cantidad=cantidad,
                    sumar=False,
                )

            if propia_sesion:

                db.commit()

            return movimientos

        except Exception:

            if propia_sesion:

                db.rollback()

            raise

        finally:

            if propia_sesion:

                db.close()

    @classmethod
    def registrar_salida_nota_credito_compra(
        cls,
        nota,
        *,
        db=None,
    ) -> list[MovimientoInventario]:

        if getattr(
            nota,
            "inventario_aplicado",
            False,
        ):

            return []

        return cls._registrar_salida_compras(
            nota,
            referencia="nota_credito_compra",
            etiqueta="NCC",
            db=db,
        )

    @classmethod
    def _registrar_salida_compras(
        cls,
        documento,
        *,
        referencia: str,
        etiqueta: str,
        db=None,
    ) -> list[MovimientoInventario]:

        propia_sesion = db is None

        if propia_sesion:

            db = SessionLocal()

        try:

            if cls._movimientos_existen(
                db,
                referencia,
                documento.id,
            ):

                return []

            bodega = cls._resolver_bodega(
                db,
                None,
            )

            movimientos: list[
                MovimientoInventario
            ] = []

            for detalle in documento.detalles:

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

                variante_id = getattr(
                    detalle,
                    "producto_variante_id",
                    None,
                )

                existencia_actual, variante = (
                    cls._obtener_existencia(
                        db,
                        producto,
                        variante_id,
                        bodega_id=bodega.id,
                    )
                )

                if existencia_actual < cantidad:

                    raise ValueError(
                        f"Stock insuficiente para "
                        f"{detalle.descripcion} "
                        f"en {bodega.codigo}.",
                    )

                costo = float(
                    detalle.precio_unitario
                    or producto.costo
                    or 0,
                )

                movimiento = MovimientoInventario(
                    bodega_id=bodega.id,
                    producto_id=producto.id,
                    producto_variante_id=variante_id,
                    tipo="salida",
                    cantidad=cantidad,
                    costo_unitario=costo,
                    referencia=referencia,
                    referencia_id=documento.id,
                    fecha=documento.fecha or date.today(),
                    observaciones=(
                        f"{etiqueta} "
                        f"{documento.numero}"
                    ),
                )

                db.add(movimiento)
                movimientos.append(movimiento)

                cls._actualizar_existencia_bodega(
                    db,
                    bodega_id=bodega.id,
                    producto=producto,
                    variante=variante,
                    cantidad=cantidad,
                    sumar=False,
                )

            if propia_sesion:

                db.commit()

            return movimientos

        except Exception:

            if propia_sesion:

                db.rollback()

            raise

        finally:

            if propia_sesion:

                db.close()
