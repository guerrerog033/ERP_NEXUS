from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String
)

from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class Marca(Base):

    __tablename__ = "marcas"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    codigo = Column(
        String(20),
        unique=True,
        nullable=False
    )

    nombre = Column(
        String(120),
        nullable=False
    )

    descripcion = Column(
        String(250)
    )

    activo = Column(
        Boolean,
        default=True,
        nullable=False
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self):

        return (
            f"<Marca("
            f"id={self.id}, "
            f"codigo='{self.codigo}', "
            f"nombre='{self.nombre}')>"
        )