from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)

from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class MedioPago(Base):

    __tablename__ = "medios_pago"

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

    codigo_dian = Column(
        String(10),
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
