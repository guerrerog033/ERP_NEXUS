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


class FacturaVenta(Base):

    __tablename__ = "facturas_venta"

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

    prefijo = Column(
        String(10),
    )

    consecutivo_dian = Column(
        String(20),
    )

    fecha = Column(
        Date,
        nullable=False,
    )

    cliente_id = Column(
        Integer,
        ForeignKey("terceros.id"),
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

    retefuente_id = Column(
        Integer,
        ForeignKey("impuestos.id"),
    )

    reteica_id = Column(
        Integer,
        ForeignKey("impuestos.id"),
    )

    reteiva_id = Column(
        Integer,
        ForeignKey("impuestos.id"),
    )

    valor_retefuente = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    valor_reteica = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    valor_reteiva = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    total = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    valor_pagado = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    saldo_pendiente = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    estado_pago = Column(
        String(20),
        nullable=False,
        default="pendiente",
    )

    fecha_vencimiento = Column(
        Date,
    )

    cufe = Column(
        String(100),
        unique=True,
    )

    estado = Column(
        String(20),
        nullable=False,
        default="borrador",
    )

    estado_dian = Column(
        String(40),
    )

    mensaje_dian = Column(
        String(500),
    )

    ruta_xml = Column(
        String(500),
    )

    ruta_zip = Column(
        String(500),
    )

    formato_impresion = Column(
        String(30),
        nullable=False,
        default="carta",
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
        "FacturaVentaDetalle",
        back_populates="factura",
        cascade="all, delete-orphan",
        order_by="FacturaVentaDetalle.orden",
    )


class FacturaVentaDetalle(Base):

    __tablename__ = "factura_venta_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    factura_id = Column(
        Integer,
        ForeignKey("facturas_venta.id"),
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

    factura = relationship(
        "FacturaVenta",
        back_populates="detalles",
    )
