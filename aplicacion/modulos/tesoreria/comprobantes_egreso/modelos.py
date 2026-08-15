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


class ComprobanteEgreso(Base):

    __tablename__ = "comprobantes_egreso"

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

    proveedor_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
    )

    forma_pago = Column(
        String(30),
        nullable=False,
        default="transferencia",
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
        "ComprobanteEgresoDetalle",
        back_populates="comprobante",
        cascade="all, delete-orphan",
        order_by="ComprobanteEgresoDetalle.orden",
    )


class ComprobanteEgresoDetalle(Base):

    __tablename__ = "comprobante_egreso_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    comprobante_id = Column(
        Integer,
        ForeignKey("comprobantes_egreso.id"),
        nullable=False,
    )

    factura_compra_id = Column(
        Integer,
        ForeignKey("facturas_compra.id"),
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

    comprobante = relationship(
        "ComprobanteEgreso",
        back_populates="detalles",
    )
