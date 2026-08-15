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


class GuiaRemisionElectronica(Base):

    __tablename__ = "guias_remision_electronica"

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

    remision_id = Column(
        Integer,
        ForeignKey("remisiones_venta.id"),
    )

    remision_numero = Column(
        String(30),
    )

    cliente_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
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

    direccion_origen = Column(
        String(250),
    )

    ciudad_origen = Column(
        String(80),
    )

    departamento_origen = Column(
        String(80),
    )

    direccion_destino = Column(
        String(250),
    )

    ciudad_destino = Column(
        String(80),
    )

    departamento_destino = Column(
        String(80),
    )

    conductor = Column(
        String(120),
    )

    vehiculo = Column(
        String(80),
    )

    placa = Column(
        String(20),
    )

    transportadora = Column(
        String(120),
    )

    cude = Column(
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
        "GuiaRemisionElectronicaDetalle",
        back_populates="guia",
        cascade="all, delete-orphan",
        order_by="GuiaRemisionElectronicaDetalle.orden",
    )


class GuiaRemisionElectronicaDetalle(Base):

    __tablename__ = "guia_remision_electronica_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    guia_id = Column(
        Integer,
        ForeignKey("guias_remision_electronica.id"),
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

    guia = relationship(
        "GuiaRemisionElectronica",
        back_populates="detalles",
    )
