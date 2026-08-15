from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
)

from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class Impuesto(Base):

    __tablename__ = "impuestos"

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

    porcentaje = Column(
        Float,
        nullable=False,
        default=0,
    )

    tipo = Column(
        String(30),
        nullable=False,
        default="IVA",
    )

    cuenta_contable = Column(
        String(30),
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
