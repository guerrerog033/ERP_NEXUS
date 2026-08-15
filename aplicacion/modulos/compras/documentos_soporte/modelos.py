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


class DocumentoSoporte(Base):

    __tablename__ = "documentos_soporte"

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

    cuds = Column(
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
        "DocumentoSoporteDetalle",
        back_populates="documento",
        cascade="all, delete-orphan",
        order_by="DocumentoSoporteDetalle.orden",
    )


class DocumentoSoporteDetalle(Base):

    __tablename__ = "documento_soporte_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    documento_id = Column(
        Integer,
        ForeignKey("documentos_soporte.id"),
        nullable=False,
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

    documento = relationship(
        "DocumentoSoporte",
        back_populates="detalles",
    )
