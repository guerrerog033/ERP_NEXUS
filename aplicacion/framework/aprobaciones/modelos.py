from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class SolicitudAprobacion(Base):

    __tablename__ = "solicitudes_aprobacion"

    id = Column(Integer, primary_key=True)
    modulo = Column(String(40), nullable=False)
    documento_id = Column(Integer, nullable=False)
    monto = Column(Float, default=0)
    aprobador_rol = Column(String(60))
    solicitante = Column(String(120))
    aprobado_por = Column(String(120))
    estado = Column(String(20), default="pendiente")
    observaciones = Column(Text)
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
