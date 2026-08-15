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
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class CuentaBancaria(Base):

    __tablename__ = "cuentas_bancarias"

    id = Column(Integer, primary_key=True)
    banco = Column(String(120), nullable=False)
    numero = Column(String(40), nullable=False)
    tipo = Column(String(30), default="corriente")
    moneda = Column(String(10), default="COP")
    saldo = Column(DINERO, default=0)
    cuenta_contable = Column(String(20))
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class LotePago(Base):

    __tablename__ = "lotes_pago"

    id = Column(Integer, primary_key=True)
    numero = Column(String(30), unique=True, nullable=False)
    cuenta_bancaria_id = Column(
        Integer,
        ForeignKey("cuentas_bancarias.id"),
    )
    fecha_programada = Column(Date)
    estado = Column(String(20), default="borrador")
    total = Column(DINERO, default=0)
    observaciones = Column(Text)
    activo = Column(Boolean, default=True)


class LotePagoDetalle(Base):

    __tablename__ = "lote_pago_detalles"

    id = Column(Integer, primary_key=True)
    lote_id = Column(
        Integer,
        ForeignKey("lotes_pago.id"),
        nullable=False,
    )
    factura_compra_id = Column(Integer)
    valor = Column(DINERO, nullable=False)
    estado = Column(String(20), default="pendiente")
