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
    DINERO,
    PORCENTAJE,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class OportunidadCRM(Base):

    __tablename__ = "crm_oportunidades"

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

    titulo = Column(
        String(200),
        nullable=False,
    )

    cliente_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
    )

    etapa = Column(
        String(30),
        nullable=False,
        default="prospeccion",
    )

    valor_estimado = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    probabilidad = Column(
        PORCENTAJE,
        nullable=False,
        default=0,
    )

    fecha_cierre_esperada = Column(
        Date,
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

    actividades = relationship(
        "ActividadCRM",
        back_populates="oportunidad",
        cascade="all, delete-orphan",
    )

    cliente = relationship(
        "Tercero",
        lazy="joined",
    )

    @property
    def cliente_nombre(self) -> str:

        if self.cliente is None:

            return ""

        return (
            self.cliente.razon_social
            or self.cliente.nombre_completo
            or ""
        )


class ActividadCRM(Base):

    __tablename__ = "crm_actividades"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    oportunidad_id = Column(
        Integer,
        ForeignKey("crm_oportunidades.id"),
        nullable=False,
    )

    tipo = Column(
        String(30),
        nullable=False,
        default="tarea",
    )

    titulo = Column(
        String(200),
        nullable=False,
    )

    descripcion = Column(
        Text,
    )

    fecha = Column(
        Date,
        nullable=False,
    )

    completada = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    oportunidad = relationship(
        "OportunidadCRM",
        back_populates="actividades",
    )

    @property
    def oportunidad_codigo(self) -> str:

        if self.oportunidad is None:

            return ""

        return self.oportunidad.codigo
