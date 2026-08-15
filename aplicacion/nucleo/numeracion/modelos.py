from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)

from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class NumeracionDocumento(Base):

    __tablename__ = "numeracion_documentos"

    __table_args__ = (
        UniqueConstraint(
            "codigo_tipo",
            "prefijo",
            name="uq_numeracion_tipo_prefijo",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    codigo_tipo = Column(
        String(40),
        nullable=False,
    )

    prefijo = Column(
        String(10),
        nullable=False,
    )

    resolucion = Column(
        String(80),
    )

    rango_desde = Column(
        Integer,
        nullable=False,
        default=1,
    )

    rango_hasta = Column(
        Integer,
        nullable=False,
        default=999999,
    )

    consecutivo_actual = Column(
        Integer,
        nullable=False,
        default=0,
    )

    fecha_inicio = Column(
        Date,
    )

    fecha_fin = Column(
        Date,
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
