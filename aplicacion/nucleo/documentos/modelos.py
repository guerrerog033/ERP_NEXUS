from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)

from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class DocumentoVinculo(Base):

    """
    Trazabilidad entre documentos comerciales.

    Ejemplo: COT-000001 → PED-000015 → REM-000008 → FV-000045
    """

    __tablename__ = "documento_vinculos"

    __table_args__ = (
        UniqueConstraint(
            "tipo_origen",
            "documento_origen_id",
            "tipo_destino",
            "documento_destino_id",
            name="uq_documento_vinculo",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    tipo_origen = Column(
        String(40),
        nullable=False,
    )

    documento_origen_id = Column(
        Integer,
        nullable=False,
    )

    tipo_destino = Column(
        String(40),
        nullable=False,
    )

    documento_destino_id = Column(
        Integer,
        nullable=False,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
