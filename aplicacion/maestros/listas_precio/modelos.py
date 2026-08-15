from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)

from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class ListaPrecio(Base):

    __tablename__ = "listas_precio"

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

    predeterminada = Column(
        Boolean,
        default=False,
        nullable=False,
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
