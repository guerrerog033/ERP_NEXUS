from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class DocumentoAdjunto(Base):

    __tablename__ = "documentos_adjuntos"

    id = Column(Integer, primary_key=True)
    modulo = Column(String(40), nullable=False)
    documento_id = Column(Integer, nullable=False)
    tipo = Column(String(30), default="soporte")
    nombre = Column(String(250), nullable=False)
    ruta = Column(String(500), nullable=False)
    descripcion = Column(Text)
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
