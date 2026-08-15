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


class ExtractoBancario(Base):

    __tablename__ = "extractos_bancarios"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    banco = Column(
        String(120),
        nullable=False,
    )

    cuenta = Column(
        String(40),
        nullable=False,
    )

    fecha = Column(
        Date,
        nullable=False,
    )

    descripcion = Column(
        String(250),
    )

    referencia = Column(
        String(80),
    )

    valor = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    tipo = Column(
        String(10),
        nullable=False,
        default="debito",
    )

    saldo = Column(
        DINERO,
    )

    conciliado = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    origen = Column(
        String(40),
        default="importacion",
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class ConciliacionBancaria(Base):

    __tablename__ = "conciliaciones_bancarias"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    extracto_id = Column(
        Integer,
        ForeignKey("extractos_bancarios.id"),
        nullable=False,
    )

    tipo_documento = Column(
        String(30),
        nullable=False,
    )

    documento_id = Column(
        Integer,
        nullable=False,
    )

    valor = Column(
        DINERO,
        nullable=False,
    )

    estado = Column(
        String(20),
        default="conciliado",
    )

    observaciones = Column(
        Text,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    extracto = relationship(
        "ExtractoBancario",
    )
