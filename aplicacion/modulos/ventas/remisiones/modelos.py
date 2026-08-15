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


class RemisionVenta(Base):

    __tablename__ = "remisiones_venta"

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

    pedido_id = Column(
        Integer,
        ForeignKey("ordenes_pedido.id"),
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

    inventario_aplicado = Column(
        Boolean,
        default=False,
        nullable=False,
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
        "RemisionVentaDetalle",
        back_populates="remision",
        cascade="all, delete-orphan",
        order_by="RemisionVentaDetalle.orden",
    )


class RemisionVentaDetalle(Base):

    __tablename__ = "remision_venta_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    remision_id = Column(
        Integer,
        ForeignKey("remisiones_venta.id"),
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

    remision = relationship(
        "RemisionVenta",
        back_populates="detalles",
    )
