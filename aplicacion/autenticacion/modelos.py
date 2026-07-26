from sqlalchemy import Column, Integer, String, Boolean

from aplicacion.base_datos.conexion import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    usuario = Column(String(50), unique=True, nullable=False)

    nombre = Column(String(150), nullable=False)

    correo = Column(String(150), unique=True)

    password = Column(String(255), nullable=False)

    activo = Column(Boolean, default=True)