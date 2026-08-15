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


class PlanCuenta(Base):

    __tablename__ = "plan_cuentas"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    codigo = Column(
        String(20),
        unique=True,
        nullable=False,
    )

    nombre = Column(
        String(200),
        nullable=False,
    )

    tipo = Column(
        String(20),
        nullable=False,
        default="activo",
    )

    activo = Column(
        Boolean,
        default=True,
        nullable=False,
    )


class AsientoContable(Base):

    __tablename__ = "asientos_contables"

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

    descripcion = Column(
        Text,
    )

    origen = Column(
        String(40),
    )

    origen_id = Column(
        Integer,
    )

    total_debito = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    total_credito = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    detalles = relationship(
        "AsientoDetalle",
        back_populates="asiento",
        cascade="all, delete-orphan",
        order_by="AsientoDetalle.orden",
    )


class AsientoDetalle(Base):

    __tablename__ = "asiento_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    asiento_id = Column(
        Integer,
        ForeignKey("asientos_contables.id"),
        nullable=False,
    )

    cuenta_id = Column(
        Integer,
        ForeignKey("plan_cuentas.id"),
        nullable=False,
    )

    debito = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    credito = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    descripcion = Column(
        String(250),
    )

    orden = Column(
        Integer,
        nullable=False,
        default=0,
    )

    asiento = relationship(
        "AsientoContable",
        back_populates="detalles",
    )

    cuenta = relationship(
        "PlanCuenta",
    )


class ReglaContabilizacion(Base):

    __tablename__ = "reglas_contabilizacion"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nombre = Column(
        String(120),
        nullable=False,
    )

    tipo_operacion = Column(
        String(40),
        nullable=False,
        default="compra",
    )

    criterio = Column(
        String(40),
        nullable=False,
        default="producto_tipo",
    )

    valor_criterio = Column(
        String(80),
        nullable=False,
        default="mercancia",
    )

    cuenta_debito = Column(
        String(20),
        nullable=False,
    )

    cuenta_credito = Column(
        String(20),
    )

    cuenta_iva = Column(
        String(20),
    )

    prioridad = Column(
        Integer,
        nullable=False,
        default=100,
    )

    activo = Column(
        Boolean,
        default=True,
        nullable=False,
    )
