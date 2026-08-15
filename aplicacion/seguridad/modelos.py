from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class AuditoriaEvento(Base):

    __tablename__ = "auditoria_eventos"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    fecha = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    usuario = Column(
        String(50),
        nullable=False,
        default="sistema",
    )

    accion = Column(
        String(40),
        nullable=False,
    )

    modulo = Column(
        String(60),
    )

    entidad = Column(
        String(80),
    )

    entidad_id = Column(
        Integer,
    )

    detalle = Column(
        Text,
    )

    exito = Column(
        Boolean,
        nullable=False,
        default=True,
    )


class AuditoriaCampo(Base):

    __tablename__ = "auditoria_cambios"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    fecha = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    usuario = Column(
        String(50),
        nullable=False,
        default="sistema",
    )

    modulo = Column(
        String(60),
    )

    entidad = Column(
        String(80),
        nullable=False,
    )

    entidad_id = Column(
        Integer,
        nullable=False,
    )

    campo = Column(
        String(80),
        nullable=False,
    )

    valor_anterior = Column(
        Text,
    )

    valor_nuevo = Column(
        Text,
    )
