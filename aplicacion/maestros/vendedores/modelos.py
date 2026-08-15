from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class Vendedor(Base):

    __tablename__ = "vendedores"

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
        String(120),
        nullable=False,
    )

    tercero_id = Column(
        Integer,
        ForeignKey("terceros.id"),
    )

    correo = Column(
        String(150),
    )

    telefono = Column(
        String(30),
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

    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
