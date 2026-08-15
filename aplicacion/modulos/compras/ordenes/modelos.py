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


class OrdenCompra(Base):

    __tablename__ = "ordenes_compra"

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

    proveedor_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
    )

    observaciones = Column(
        Text,
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
        String(30),
        nullable=False,
        default="pendiente",
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
        "OrdenCompraDetalle",
        back_populates="orden",
        cascade="all, delete-orphan",
        order_by="OrdenCompraDetalle.linea_orden",
    )


class OrdenCompraDetalle(Base):

    __tablename__ = "orden_compra_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    orden_id = Column(
        Integer,
        ForeignKey("ordenes_compra.id"),
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

    cantidad_recibida = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    costo_unitario = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    total_linea = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    linea_orden = Column(
        Integer,
        nullable=False,
        default=0,
    )

    orden = relationship(
        "OrdenCompra",
        back_populates="detalles",
    )


class RecepcionCompra(Base):

    __tablename__ = "recepciones_compra"

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

    orden_id = Column(
        Integer,
        ForeignKey("ordenes_compra.id"),
        nullable=False,
    )

    bodega_id = Column(
        Integer,
        ForeignKey("bodegas.id"),
        nullable=False,
    )

    observaciones = Column(
        Text,
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
        "RecepcionCompraDetalle",
        back_populates="recepcion",
        cascade="all, delete-orphan",
    )


class RecepcionCompraDetalle(Base):

    __tablename__ = "recepcion_compra_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    recepcion_id = Column(
        Integer,
        ForeignKey("recepciones_compra.id"),
        nullable=False,
    )

    orden_detalle_id = Column(
        Integer,
        ForeignKey("orden_compra_detalles.id"),
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

    cantidad = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    costo_unitario = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    recepcion = relationship(
        "RecepcionCompra",
        back_populates="detalles",
    )
