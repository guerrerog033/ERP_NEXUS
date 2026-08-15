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
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base
from aplicacion.base_datos.tipos import (
    CANTIDAD,
    DINERO,
)


class NotaCreditoCompra(Base):

    __tablename__ = "notas_credito_compra"

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

    factura_compra_id = Column(
        Integer,
        ForeignKey("facturas_compra.id"),
        nullable=False,
    )

    motivo = Column(
        String(250),
    )

    factura_cufe = Column(
        String(100),
    )

    cufe = Column(
        String(100),
    )

    subtotal = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    iva = Column(
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
        default="borrador",
    )

    contabilizado = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    inventario_aplicado = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    asiento_id = Column(
        Integer,
        ForeignKey("asientos_contables.id"),
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
        "NotaCreditoCompraDetalle",
        back_populates="nota_credito",
        cascade="all, delete-orphan",
        order_by="NotaCreditoCompraDetalle.orden",
    )


class NotaCreditoCompraDetalle(Base):

    __tablename__ = "nota_credito_compra_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nota_credito_id = Column(
        Integer,
        ForeignKey("notas_credito_compra.id"),
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

    nota_credito = relationship(
        "NotaCreditoCompra",
        back_populates="detalles",
    )
