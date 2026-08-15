from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.types import JSON

from aplicacion.base_datos.conexion import Base


class SerialLicencia(Base):

    __tablename__ = "seriales_licencia"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    serial = Column(
        String(30),
        unique=True,
        nullable=False,
    )

    edicion = Column(
        String(30),
        nullable=False,
    )

    modulos = Column(
        JSON,
        nullable=False,
        default=list,
    )

    max_usuarios = Column(
        Integer,
        nullable=False,
        default=1,
    )

    dias_validez = Column(
        Integer,
    )

    titular_esperado = Column(
        String(200),
    )

    estado = Column(
        String(20),
        nullable=False,
        default="disponible",
    )

    fecha_creacion = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    activacion_id = Column(
        Integer,
        ForeignKey("licencias_activacion.id"),
    )


class LicenciaActivacion(Base):

    __tablename__ = "licencias_activacion"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    serial = Column(
        String(30),
        unique=True,
        nullable=False,
    )

    edicion = Column(
        String(30),
        nullable=False,
    )

    titular = Column(
        String(200),
    )

    nit_cliente = Column(
        String(30),
    )

    modulos = Column(
        JSON,
        nullable=False,
        default=list,
    )

    max_usuarios = Column(
        Integer,
        nullable=False,
        default=1,
    )

    fecha_activacion = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    fecha_vencimiento = Column(
        DateTime,
    )

    huella_equipo = Column(
        String(128),
        nullable=False,
    )

    estado = Column(
        String(20),
        nullable=False,
        default="activa",
    )

    activa = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    notas = Column(
        Text,
    )
