from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from aplicacion.base_datos.tipos import (
    CANTIDAD,
    DINERO,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class OrdenPedido(Base):

    __tablename__ = "ordenes_pedido"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    numero = Column(
        String(30),
        unique=True,
        nullable=False,
    )

    fecha = Column(
        Date,
        nullable=False,
    )

    cotizacion_id = Column(
        Integer,
        ForeignKey("cotizaciones.id"),
    )

    cliente_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
    )

    observaciones = Column(
        Text,
    )

    vendedor = Column(
        String(120),
    )

    subtotal = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    total = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    estado = Column(
        String(20),
        nullable=False,
        default="pendiente",
    )

    reserva_aplicada = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    bodega_id = Column(
        Integer,
        ForeignKey("bodegas.id"),
    )

    activo = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    detalles = relationship(
        "OrdenPedidoDetalle",
        back_populates="pedido",
        cascade="all, delete-orphan",
        order_by="OrdenPedidoDetalle.orden",
    )


class OrdenPedidoDetalle(Base):

    __tablename__ = "orden_pedido_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    pedido_id = Column(
        Integer,
        ForeignKey("ordenes_pedido.id"),
        nullable=False,
    )

    producto_id = Column(
        Integer,
        ForeignKey("productos.id"),
    )

    producto_variante_id = Column(
        Integer,
        ForeignKey("producto_variantes.id"),
    )

    descripcion = Column(
        String(250),
        nullable=False,
    )

    cantidad = Column(
        CANTIDAD,
        nullable=False,
        default=1,
    )

    precio_unitario = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    impuesto_id = Column(
        Integer,
        ForeignKey("impuestos.id"),
    )

    precio_incluye_iva = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    total_linea = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    orden = Column(
        Integer,
        nullable=False,
        default=0,
    )

    pedido = relationship(
        "OrdenPedido",
        back_populates="detalles",
    )


class PedidoReserva(Base):

    __tablename__ = "pedido_reservas"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    pedido_id = Column(
        Integer,
        ForeignKey("ordenes_pedido.id"),
        nullable=False,
    )

    bodega_id = Column(
        Integer,
        ForeignKey("bodegas.id"),
        nullable=False,
    )

    producto_id = Column(
        Integer,
        ForeignKey("productos.id"),
        nullable=False,
    )

    producto_variante_id = Column(
        Integer,
        ForeignKey("producto_variantes.id"),
    )

    cantidad = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    activo = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
