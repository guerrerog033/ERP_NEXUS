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

from aplicacion.base_datos.tipos import DINERO
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class ReciboCaja(Base):

    __tablename__ = "recibos_caja"

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

    fecha = Column(
        Date,
        nullable=False,
    )

    cliente_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
    )

    forma_pago = Column(
        String(30),
        nullable=False,
        default="efectivo",
    )

    valor_total = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    estado = Column(
        String(20),
        nullable=False,
        default="borrador",
    )

    formato_impresion = Column(
        String(20),
        nullable=False,
        default="carta",
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
        "ReciboCajaDetalle",
        back_populates="recibo",
        cascade="all, delete-orphan",
        order_by="ReciboCajaDetalle.orden",
    )


class ReciboCajaDetalle(Base):

    __tablename__ = "recibo_caja_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    recibo_id = Column(
        Integer,
        ForeignKey("recibos_caja.id"),
        nullable=False,
    )

    factura_venta_id = Column(
        Integer,
        ForeignKey("facturas_venta.id"),
        nullable=False,
    )

    valor_aplicado = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    orden = Column(
        Integer,
        nullable=False,
        default=0,
    )

    recibo = relationship(
        "ReciboCaja",
        back_populates="detalles",
    )
