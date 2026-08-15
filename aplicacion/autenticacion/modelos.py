from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from aplicacion.base_datos.conexion import Base


class Rol(Base):

    __tablename__ = "roles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    codigo = Column(
        String(30),
        unique=True,
        nullable=False,
    )

    nombre = Column(
        String(100),
        nullable=False,
    )

    modulos = Column(
        JSON,
        nullable=False,
        default=list,
    )

    activo = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    usuarios = relationship(
        "Usuario",
        back_populates="rol",
    )

    @property
    def resumen_modulos(self) -> str:

        modulos = list(
            self.modulos or [],
        )

        if "*" in modulos:

            return "Acceso total"

        if not modulos:

            return "Sin módulos"

        return f"{len(modulos)} módulo(s)"


class Usuario(Base):

    __tablename__ = "usuarios"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    usuario = Column(
        String(50),
        unique=True,
        nullable=False,
    )

    nombre = Column(
        String(150),
        nullable=False,
    )

    correo = Column(
        String(150),
        unique=True,
    )

    password = Column(
        String(255),
        nullable=False,
    )

    rol_id = Column(
        Integer,
        ForeignKey("roles.id"),
    )

    activo = Column(
        Boolean,
        default=True,
    )

    rol = relationship(
        "Rol",
        back_populates="usuarios",
    )

    @property
    def rol_nombre(self) -> str:

        from sqlalchemy import inspect as sa_inspect

        estado = sa_inspect(
            self,
        )

        if "rol" in estado.unloaded:

            return ""

        if self.rol is None:

            return ""

        return self.rol.nombre or ""
