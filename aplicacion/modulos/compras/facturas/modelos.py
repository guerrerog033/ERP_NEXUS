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


class FacturaCompra(Base):

    __tablename__ = "facturas_compra"

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
    )

    nit_proveedor = Column(
        String(20),
    )

    razon_social_proveedor = Column(
        String(250),
    )

    numero_proveedor = Column(
        String(40),
    )

    prefijo = Column(
        String(10),
    )

    consecutivo = Column(
        String(20),
    )

    cufe = Column(
        String(100),
        unique=True,
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

    es_credito = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    fecha_vencimiento = Column(
        Date,
    )

    requiere_acuse_recibo = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    acuse_recibo_estado = Column(
        String(30),
        nullable=False,
        default="no_aplica",
    )

    acuse_recibo_cude = Column(
        String(100),
    )

    acuse_recibo_fecha = Column(
        DateTime(timezone=True),
    )

    acuse_recibo_mensaje = Column(
        String(500),
    )

    ruta_acuse_xml = Column(
        String(500),
    )

    evento_radian_codigo = Column(
        String(10),
    )

    evento_radian_cude = Column(
        String(100),
    )

    evento_radian_mensaje = Column(
        String(500),
    )

    evento_radian_fecha = Column(
        DateTime(timezone=True),
    )

    origen = Column(
        String(20),
        nullable=False,
        default="manual",
    )

    ruta_xml = Column(
        String(500),
    )

    observaciones = Column(
        Text,
    )

    estado = Column(
        String(20),
        nullable=False,
        default="recibida",
    )

    formato_impresion = Column(
        String(20),
        nullable=False,
        default="carta",
    )

    cufe_validado = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    cufe_estado_dian = Column(
        String(40),
    )

    cufe_validado_en = Column(
        DateTime(timezone=True),
    )

    cufe_mensaje_dian = Column(
        String(500),
    )

    contabilizado = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    asiento_id = Column(
        Integer,
        ForeignKey("asientos_contables.id"),
    )

    orden_compra_id = Column(
        Integer,
        ForeignKey("ordenes_compra.id"),
    )

    inventario_aplicado = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    match_estado = Column(
        String(30),
    )

    match_mensaje = Column(
        String(500),
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
        "FacturaCompraDetalle",
        back_populates="factura",
        cascade="all, delete-orphan",
        order_by="FacturaCompraDetalle.orden",
    )

    eventos_radian = relationship(
        "FacturaCompraEventoRadian",
        back_populates="factura",
        cascade="all, delete-orphan",
        order_by="FacturaCompraEventoRadian.fecha_evento.desc()",
    )


class FacturaCompraEventoRadian(Base):

    __tablename__ = "factura_compra_eventos_radian"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    factura_id = Column(
        Integer,
        ForeignKey("facturas_compra.id"),
        nullable=False,
    )

    codigo_evento = Column(
        String(10),
        nullable=False,
    )

    cude = Column(
        String(100),
    )

    estado = Column(
        String(30),
        nullable=False,
        default="enviado",
    )

    mensaje = Column(
        String(500),
    )

    ruta_xml = Column(
        String(500),
    )

    forzado = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    fecha_evento = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    factura = relationship(
        "FacturaCompra",
        back_populates="eventos_radian",
    )


class FacturaCompraDetalle(Base):

    __tablename__ = "factura_compra_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    factura_id = Column(
        Integer,
        ForeignKey("facturas_compra.id"),
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

    orden_detalle_id = Column(
        Integer,
        ForeignKey("orden_compra_detalles.id"),
    )

    factura = relationship(
        "FacturaCompra",
        back_populates="detalles",
    )
