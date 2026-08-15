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

from aplicacion.base_datos.tipos import (
    CANTIDAD,
    DINERO,
    PORCENTAJE,
    TASA,
)
from aplicacion.base_datos.conexion import Base


class Proforma(Base):

    __tablename__ = "proformas"

    id = Column(Integer, primary_key=True)
    numero = Column(String(30), unique=True, nullable=False)
    fecha = Column(Date, nullable=False)
    cliente_id = Column(Integer, ForeignKey("terceros.id"))
    moneda = Column(String(10), default="COP")
    tasa_cambio = Column(TASA, default=1)
    fecha_vigencia = Column(Date)
    condiciones = Column(Text)
    observaciones = Column(Text)
    subtotal = Column(DINERO, default=0)
    total = Column(DINERO, default=0)
    estado = Column(String(20), default="borrador")
    version = Column(Integer, default=1)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    detalles = relationship(
        "ProformaDetalle",
        back_populates="proforma",
        cascade="all, delete-orphan",
    )


class ProformaDetalle(Base):

    __tablename__ = "proforma_detalles"

    id = Column(Integer, primary_key=True)
    proforma_id = Column(
        Integer,
        ForeignKey("proformas.id"),
        nullable=False,
    )
    producto_id = Column(Integer, ForeignKey("productos.id"))
    descripcion = Column(String(250), nullable=False)
    cantidad = Column(CANTIDAD, default=1)
    precio_unitario = Column(DINERO, default=0)
    descuento_porcentaje = Column(PORCENTAJE, default=0)
    total_linea = Column(DINERO, default=0)
    ficha_tecnica = Column(Text)
    orden = Column(Integer, default=0)

    proforma = relationship(
        "Proforma",
        back_populates="detalles",
    )
