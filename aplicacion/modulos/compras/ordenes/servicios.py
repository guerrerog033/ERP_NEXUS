from __future__ import annotations

from datetime import date

from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.productos.modelos import (
    Producto,
    ProductoVariante,
)
from aplicacion.maestros.terceros.modelos import Tercero

from .modelos import (
    OrdenCompra,
    OrdenCompraDetalle,
    RecepcionCompra,
    RecepcionCompraDetalle,
)
from .repositorio import (
    RepositorioOrdenCompra,
    RepositorioRecepcionCompra,
)


class ServicioOrdenCompra:

    PREFIJO = "OC"
    PREFIJO_REC = "REC"
    LONGITUD = 6

    @classmethod
    def generar_numero(
        cls,
        *,
        prefijo: str | None = None,
    ) -> str:

        prefijo = prefijo or cls.PREFIJO

        if prefijo == cls.PREFIJO_REC:

            secuencia = (
                RepositorioRecepcionCompra
                .siguiente_secuencia(
                    prefijo,
                )
            )

        else:

            secuencia = (
                RepositorioOrdenCompra
                .siguiente_secuencia(
                    prefijo,
                )
            )

        return (
            f"{prefijo}"
            f"{secuencia:0{cls.LONGITUD}d}"
        )

    @classmethod
    def listar(
        cls,
    ) -> list[dict]:

        db = SessionLocal()

        try:

            ordenes = (
                db.query(OrdenCompra)
                .filter(
                    OrdenCompra.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    OrdenCompra.fecha.desc(),
                    OrdenCompra.numero.desc(),
                )
                .all()
            )

            proveedor_ids = {
                orden.proveedor_id
                for orden in ordenes
            }

            proveedores = {

                tercero.id: tercero

                for tercero in (
                    db.query(Tercero)
                    .filter(
                        Tercero.id.in_(
                            proveedor_ids,
                        ),
                    )
                    .all()
                )

            } if proveedor_ids else {}

            filas: list[dict] = []

            for orden in ordenes:

                proveedor = proveedores.get(
                    orden.proveedor_id,
                )

                nombre = ""

                if proveedor is not None:

                    nombre = (
                        proveedor.nombre_comercial
                        or proveedor.razon_social
                        or proveedor.nombre_completo
                        or ""
                    ).strip()

                filas.append(
                    {
                        "id": orden.id,
                        "numero": orden.numero,
                        "fecha": orden.fecha,
                        "proveedor": nombre,
                        "total": float(
                            orden.total or 0,
                        ),
                        "estado": orden.estado,
                    },
                )

            return filas

        finally:

            db.close()

    @classmethod
    def obtener_completa(
        cls,
        orden_id: int,
    ):

        return RepositorioOrdenCompra.obtener_completa(
            orden_id,
        )

    @classmethod
    def datos_impresion(
        cls,
        orden_id: int,
    ) -> tuple:

        db = SessionLocal()

        try:

            orden = (
                db.query(OrdenCompra)
                .options(
                    joinedload(
                        OrdenCompra.detalles,
                    ),
                )
                .filter(
                    OrdenCompra.id == orden_id,
                )
                .first()
            )

            if orden is None:

                raise ValueError(
                    "Orden no encontrada.",
                )

            proveedor = (
                db.query(Tercero)
                .filter(
                    Tercero.id
                    == orden.proveedor_id,
                )
                .first()
            )

            nombre = ""

            if proveedor is not None:

                nombre = (
                    proveedor.nombre_comercial
                    or proveedor.razon_social
                    or proveedor.nombre_completo
                    or ""
                ).strip()

            return (
                orden,
                list(
                    orden.detalles or [],
                ),
                nombre,
                proveedor,
            )

        finally:

            db.close()

    @classmethod
    def listar_pendientes_recepcion(
        cls,
    ) -> list[OrdenCompra]:

        return RepositorioOrdenCompra.listar_pendientes_recepcion()

    @classmethod
    def listar_recepciones(
        cls,
        *,
        limite: int = 100,
    ) -> list[dict]:

        db = SessionLocal()

        try:

            recepciones = (
                db.query(RecepcionCompra)
                .join(
                    OrdenCompra,
                    RecepcionCompra.orden_id
                    == OrdenCompra.id,
                )
                .filter(
                    RecepcionCompra.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    RecepcionCompra.fecha.desc(),
                    RecepcionCompra.numero.desc(),
                )
                .limit(limite)
                .all()
            )

            filas: list[dict] = []

            for recepcion in recepciones:

                orden = (
                    db.query(OrdenCompra)
                    .filter(
                        OrdenCompra.id
                        == recepcion.orden_id,
                    )
                    .first()
                )

                cantidad_total = sum(
                    float(
                        detalle.cantidad or 0,
                    )
                    for detalle in (
                        recepcion.detalles or []
                    )
                )

                filas.append(
                    {
                        "id": recepcion.id,
                        "numero": recepcion.numero,
                        "fecha": recepcion.fecha,
                        "orden_numero": (
                            orden.numero
                            if orden
                            else ""
                        ),
                        "cantidad_total": cantidad_total,
                        "observaciones": (
                            recepcion.observaciones
                            or ""
                        ),
                        "activo": recepcion.activo,
                    },
                )

            return filas

        finally:

            db.close()

    @classmethod
    def guardar(
        cls,
        *,
        proveedor_id: int,
        fecha: date,
        observaciones: str = "",
        lineas: list[dict],
        orden_id: int | None = None,
    ) -> OrdenCompra:

        if not proveedor_id:

            raise ValueError(
                "Seleccione un proveedor.",
            )

        if not lineas:

            raise ValueError(
                "Agregue al menos una línea.",
            )

        db = SessionLocal()

        try:

            if orden_id:

                orden = (
                    db.query(OrdenCompra)
                    .options(
                        joinedload(
                            OrdenCompra.detalles,
                        ),
                    )
                    .filter(
                        OrdenCompra.id
                        == orden_id,
                    )
                    .first()
                )

                if orden is None:

                    raise ValueError(
                        "Orden no encontrada.",
                    )

                if orden.estado not in (
                    "pendiente",
                ):

                    raise ValueError(
                        "Solo se pueden editar órdenes pendientes.",
                    )

                orden.detalles.clear()

            else:

                orden = OrdenCompra(
                    numero=cls.generar_numero(),
                    fecha=fecha,
                    proveedor_id=proveedor_id,
                    observaciones=observaciones,
                    estado="pendiente",
                    activo=True,
                )

                db.add(orden)
                db.flush()

            subtotal = 0.0

            for indice, linea in enumerate(
                lineas,
            ):

                cantidad = float(
                    linea.get(
                        "cantidad",
                        0,
                    )
                    or 0,
                )

                costo = float(
                    linea.get(
                        "costo_unitario",
                        0,
                    )
                    or 0,
                )

                if cantidad <= 0:

                    raise ValueError(
                        "La cantidad debe ser mayor a cero.",
                    )

                total_linea = cantidad * costo
                subtotal += total_linea

                db.add(
                    OrdenCompraDetalle(
                        orden_id=orden.id,
                        producto_id=linea.get(
                            "producto_id",
                        ),
                        producto_variante_id=linea.get(
                            "producto_variante_id",
                        ),
                        descripcion=str(
                            linea.get(
                                "descripcion",
                                "",
                            )
                            or "Producto",
                        ).strip(),
                        cantidad=cantidad,
                        costo_unitario=costo,
                        total_linea=total_linea,
                        linea_orden=indice,
                    ),
                )

            orden.fecha = fecha
            orden.proveedor_id = proveedor_id
            orden.observaciones = observaciones
            orden.subtotal = subtotal
            orden.total = subtotal

            db.commit()
            db.refresh(orden)

            return orden

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def _actualizar_estado(
        cls,
        orden: OrdenCompra,
    ) -> None:

        pendiente = False
        recibido_total = True

        for detalle in orden.detalles:

            faltante = float(
                detalle.cantidad or 0,
            ) - float(
                detalle.cantidad_recibida
                or 0,
            )

            if faltante > 0:

                pendiente = True
                recibido_total = False

        if recibido_total:

            orden.estado = "recibida"

        elif pendiente and any(
            float(
                detalle.cantidad_recibida
                or 0,
            )
            > 0
            for detalle in orden.detalles
        ):

            orden.estado = "parcial"

        else:

            orden.estado = "pendiente"

    @classmethod
    def registrar_recepcion(
        cls,
        *,
        orden_id: int,
        bodega_id: int,
        fecha: date,
        lineas: list[dict],
        observaciones: str = "",
    ) -> RecepcionCompra:

        if not lineas:

            raise ValueError(
                "Indique cantidades a recibir.",
            )

        db = SessionLocal()

        try:

            orden = (
                db.query(OrdenCompra)
                .options(
                    joinedload(
                        OrdenCompra.detalles,
                    ),
                )
                .filter(
                    OrdenCompra.id == orden_id,
                )
                .first()
            )

            if orden is None:

                raise ValueError(
                    "Orden no encontrada.",
                )

            db.refresh(
                orden,
            )

            detalles_map = {
                detalle.id: detalle
                for detalle in (
                    db.query(OrdenCompraDetalle)
                    .filter(
                        OrdenCompraDetalle.orden_id
                        == orden_id,
                    )
                    .all()
                )
            }

            recepcion = RecepcionCompra(
                numero=cls.generar_numero(
                    prefijo=cls.PREFIJO_REC,
                ),
                fecha=fecha,
                orden_id=orden_id,
                bodega_id=bodega_id,
                observaciones=observaciones,
                activo=True,
            )

            db.add(recepcion)
            db.flush()

            for linea in lineas:

                detalle_id = linea.get(
                    "orden_detalle_id",
                )

                cantidad = float(
                    linea.get(
                        "cantidad",
                        0,
                    )
                    or 0,
                )

                if cantidad <= 0:

                    continue

                detalle = detalles_map.get(
                    detalle_id,
                )

                if detalle is None:

                    raise ValueError(
                        "Línea de orden inválida.",
                    )

                pendiente = float(
                    detalle.cantidad or 0,
                ) - float(
                    detalle.cantidad_recibida
                    or 0,
                )

                if cantidad > pendiente + 0.0001:

                    raise ValueError(
                        f"Cantidad excede lo pendiente en "
                        f"{detalle.descripcion}.",
                    )

                costo = float(
                    detalle.costo_unitario or 0,
                )

                db.add(
                    RecepcionCompraDetalle(
                        recepcion_id=recepcion.id,
                        orden_detalle_id=detalle.id,
                        producto_id=detalle.producto_id,
                        producto_variante_id=(
                            detalle.producto_variante_id
                        ),
                        cantidad=cantidad,
                        costo_unitario=costo,
                    ),
                )

                detalle.cantidad_recibida = float(
                    detalle.cantidad_recibida
                    or 0,
                ) + cantidad

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
                    or producto.tipo
                    == "servicio"
                ):

                    continue

                from aplicacion.modulos.inventario.servicios import (
                    ServicioInventario,
                )

                ServicioInventario.registrar_entrada(
                    db,
                    bodega_id=bodega_id,
                    producto=producto,
                    producto_variante_id=(
                        detalle.producto_variante_id
                    ),
                    cantidad=cantidad,
                    costo_unitario=costo,
                    referencia="recepcion_compra",
                    referencia_id=recepcion.id,
                    fecha=fecha,
                    observaciones=(
                        f"REC {recepcion.numero} "
                        f"OC {orden.numero}"
                    ),
                )

            db.flush()

            orden_refreshed = (
                db.query(OrdenCompra)
                .filter(
                    OrdenCompra.id == orden_id,
                )
                .first()
            )

            if orden_refreshed is not None:

                db.refresh(
                    orden_refreshed,
                )

                detalles_actualizados = (
                    db.query(OrdenCompraDetalle)
                    .filter(
                        OrdenCompraDetalle.orden_id
                        == orden_id,
                    )
                    .all()
                )

                orden_refreshed.detalles = (
                    detalles_actualizados
                )

                cls._actualizar_estado(
                    orden_refreshed,
                )

            db.commit()
            db.refresh(recepcion)

            from aplicacion.modulos.compras.integracion_oc import (
                ServicioIntegracionCompras,
            )

            ServicioIntegracionCompras.procesar_radian_tras_recepcion(
                orden_id,
            )

            return recepcion

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def anular_recepcion(
        cls,
        recepcion_id: int,
        *,
        motivo: str = "",
    ) -> RecepcionCompra:

        db = SessionLocal()

        try:

            recepcion = (
                db.query(RecepcionCompra)
                .options(
                    joinedload(
                        RecepcionCompra.detalles,
                    ),
                )
                .filter(
                    RecepcionCompra.id
                    == recepcion_id,
                )
                .first()
            )

            if recepcion is None:

                raise ValueError(
                    "Recepción no encontrada.",
                )

            if not recepcion.activo:

                raise ValueError(
                    "La recepción ya está anulada.",
                )

            from aplicacion.modulos.inventario.servicios import (
                ServicioInventario,
            )

            ServicioInventario.revertir_recepcion_compra(
                recepcion,
                db=db,
            )

            for detalle in recepcion.detalles:

                orden_detalle = (
                    db.query(
                        OrdenCompraDetalle,
                    )
                    .filter(
                        OrdenCompraDetalle.id
                        == detalle.orden_detalle_id,
                    )
                    .first()
                )

                if orden_detalle is None:

                    continue

                orden_detalle.cantidad_recibida = max(
                    float(
                        orden_detalle.cantidad_recibida
                        or 0,
                    )
                    - float(
                        detalle.cantidad or 0,
                    ),
                    0.0,
                )

            recepcion.activo = False

            texto = (
                motivo.strip()
                or "Anulada"
            )

            recepcion.observaciones = (
                f"{recepcion.observaciones or ''} "
                f"[ANULADA: {texto}]"
            ).strip()

            orden = (
                db.query(OrdenCompra)
                .options(
                    joinedload(
                        OrdenCompra.detalles,
                    ),
                )
                .filter(
                    OrdenCompra.id
                    == recepcion.orden_id,
                )
                .first()
            )

            if orden is not None:

                cls._actualizar_estado(
                    orden,
                )

            db.commit()
            db.refresh(recepcion)

            return recepcion

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
