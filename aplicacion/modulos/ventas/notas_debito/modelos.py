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


class NotaDebitoVenta(Base):

    __tablename__ = "notas_debito_venta"

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

    factura_id = Column(
        Integer,
        ForeignKey("facturas_venta.id"),
        nullable=False,
    )

    motivo = Column(
        String(250),
    )

    factura_cufe = Column(
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

    contabilizado = Column(
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
        "NotaDebitoVentaDetalle",
        back_populates="nota_debito",
        cascade="all, delete-orphan",
        order_by="NotaDebitoVentaDetalle.orden",
    )


class NotaDebitoVentaDetalle(Base):

    __tablename__ = "nota_debito_venta_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nota_debito_id = Column(
        Integer,
        ForeignKey("notas_debito_venta.id"),
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

    nota_debito = relationship(
        "NotaDebitoVenta",
        back_populates="detalles",
    )
