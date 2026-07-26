from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)

    nit = Column(String(20), unique=True, nullable=False)

    razon_social = Column(String(200), nullable=False)

    nombre_comercial = Column(String(200))

    telefono = Column(String(30))

    correo = Column(String(120))

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )