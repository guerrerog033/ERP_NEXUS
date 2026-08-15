from __future__ import annotations

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.productos.modelos import Producto
from aplicacion.modulos.inventario.servicios import (
    ServicioInventario,
)
from aplicacion.modulos.ventas.pedidos.modelos import (
    OrdenPedido,
    PedidoReserva,
)
from aplicacion.nucleo.configuracion import Configuracion


class ServicioReservaPedido:

    @classmethod
    def reserva_habilitada(cls) -> bool:

        valor = Configuracion.obtener(
            "ventas",
            "reservar_stock_pedido",
        )

        if valor is None:

            return True

        return bool(
            valor,
        )

    @classmethod
    def reservar(
        cls,
        pedido_id: int,
        *,
        bodega_id: int | None = None,
    ) -> OrdenPedido:

        if not cls.reserva_habilitada():

            raise ValueError(
                "La reserva de stock está deshabilitada.",
            )

        db = SessionLocal()

        try:

            pedido = (
                db.query(OrdenPedido)
                .filter(
                    OrdenPedido.id == pedido_id,
                )
                .first()
            )

            if pedido is None:

                raise ValueError(
                    "No se encontró el pedido.",
                )

            if pedido.estado == "borrador":

                raise ValueError(
                    "Confirme el pedido antes de reservar stock.",
                )

            if pedido.reserva_aplicada:

                raise ValueError(
                    "El pedido ya tiene reserva activa.",
                )

            bodega = ServicioInventario._bodega_operacion(
                db,
                contexto="ventas",
                bodega_id=(
                    bodega_id
                    or pedido.bodega_id
                ),
            )

            for detalle in pedido.detalles:

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

                disponible = (
                    ServicioInventario
                    ._disponible_bodega(
                        db,
                        bodega_id=bodega.id,
                        producto_id=producto.id,
                        producto_variante_id=(
                            detalle.producto_variante_id
                        ),
                    )
                )

                if disponible < cantidad:

                    raise ValueError(
                        f"Stock disponible insuficiente "
                        f"para {detalle.descripcion} "
                        f"(disponible {disponible:g}).",
                    )

                registro = (
                    ServicioInventario
                    ._buscar_existencia_bodega(
                        db,
                        bodega_id=bodega.id,
                        producto_id=producto.id,
                        producto_variante_id=(
                            detalle.producto_variante_id
                        ),
                    )
                )

                if registro is None:

                    raise ValueError(
                        f"Sin existencia en bodega "
                        f"para {detalle.descripcion}.",
                    )

                registro.cantidad_reservada = float(
                    registro.cantidad_reservada
                    or 0,
                ) + cantidad

                db.add(
                    PedidoReserva(
                        pedido_id=pedido.id,
                        bodega_id=bodega.id,
                        producto_id=producto.id,
                        producto_variante_id=(
                            detalle.producto_variante_id
                        ),
                        cantidad=cantidad,
                        activo=True,
                    ),
                )

            pedido.reserva_aplicada = True
            pedido.bodega_id = bodega.id
            pedido.estado = "reservado"

            db.commit()
            db.refresh(pedido)

            return pedido

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def liberar(
        cls,
        pedido_id: int,
    ) -> OrdenPedido:

        db = SessionLocal()

        try:

            pedido = (
                db.query(OrdenPedido)
                .filter(
                    OrdenPedido.id == pedido_id,
                )
                .first()
            )

            if pedido is None:

                raise ValueError(
                    "No se encontró el pedido.",
                )

            if not pedido.reserva_aplicada:

                raise ValueError(
                    "El pedido no tiene reserva activa.",
                )

            reservas = (
                db.query(PedidoReserva)
                .filter(
                    PedidoReserva.pedido_id
                    == pedido_id,
                    PedidoReserva.activo.is_(
                        True,
                    ),
                )
                .all()
            )

            for reserva in reservas:

                registro = (
                    ServicioInventario
                    ._buscar_existencia_bodega(
                        db,
                        bodega_id=reserva.bodega_id,
                        producto_id=reserva.producto_id,
                        producto_variante_id=(
                            reserva.producto_variante_id
                        ),
                    )
                )

                if registro is not None:

                    registro.cantidad_reservada = max(
                        0,
                        float(
                            registro.cantidad_reservada
                            or 0,
                        )
                        - float(
                            reserva.cantidad or 0,
                        ),
                    )

                reserva.activo = False

            pedido.reserva_aplicada = False

            if pedido.estado == "reservado":

                pedido.estado = "pendiente"

            db.commit()
            db.refresh(pedido)

            return pedido

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def consumir_por_salida(
        cls,
        db,
        *,
        pedido_id: int,
        producto_id: int,
        producto_variante_id: int | None,
        bodega_id: int,
        cantidad: float,
    ) -> None:

        if cantidad <= 0:

            return

        pendiente = cantidad

        reservas = (
            db.query(PedidoReserva)
            .filter(
                PedidoReserva.pedido_id
                == pedido_id,
                PedidoReserva.bodega_id
                == bodega_id,
                PedidoReserva.producto_id
                == producto_id,
                PedidoReserva.activo.is_(
                    True,
                ),
            )
            .all()
        )

        for reserva in reservas:

            if pendiente <= 0:

                break

            if (
                reserva.producto_variante_id
                != producto_variante_id
            ):

                continue

            reservado = float(
                reserva.cantidad or 0,
            )

            if reservado <= 0:

                continue

            consumir = min(
                pendiente,
                reservado,
            )

            reserva.cantidad = reservado - consumir

            if reserva.cantidad <= 0:

                reserva.activo = False

            registro = (
                ServicioInventario
                ._buscar_existencia_bodega(
                    db,
                    bodega_id=bodega_id,
                    producto_id=producto_id,
                    producto_variante_id=(
                        producto_variante_id
                    ),
                )
            )

            if registro is not None:

                registro.cantidad_reservada = max(
                    0,
                    float(
                        registro.cantidad_reservada
                        or 0,
                    )
                    - consumir,
                )

            pendiente -= consumir

        pedido = (
            db.query(OrdenPedido)
            .filter(
                OrdenPedido.id == pedido_id,
            )
            .first()
        )

        if pedido is None:

            return

        activas = (
            db.query(PedidoReserva.id)
            .filter(
                PedidoReserva.pedido_id
                == pedido_id,
                PedidoReserva.activo.is_(
                    True,
                ),
            )
            .first()
        )

        if activas is None:

            pedido.reserva_aplicada = False

            if pedido.estado == "reservado":

                pedido.estado = "pendiente"
