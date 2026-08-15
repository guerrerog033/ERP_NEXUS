from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class Empresa(Base):

    __tablename__ = "empresa"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # ==========================
    # Información general
    # ==========================

    razon_social = Column(
        String(200),
        nullable=False
    )

    nombre_comercial = Column(
        String(200)
    )

    nit = Column(
        String(20),
        nullable=False,
        unique=True
    )

    dv = Column(
        String(2)
    )

    # ==========================
    # Dirección
    # ==========================

    direccion = Column(
        String(200)
    )

    pais = Column(
        String(100),
        default="Colombia"
    )

    departamento = Column(
        String(100)
    )

    ciudad = Column(
        String(100)
    )

    # ==========================
    # Contacto
    # ==========================

    telefono = Column(
        String(30)
    )

    celular = Column(
        String(30)
    )

    correo = Column(
        String(150)
    )

    sitio_web = Column(
        String(150)
    )

    logo_ruta = Column(
        String(500),
    )

    # ==========================
    # Información legal
    # ==========================

    representante_legal = Column(
        String(200)
    )

    actividad_economica = Column(
        String(150)
    )

    regimen_tributario = Column(
        String(100)
    )

    responsable_iva = Column(
        Boolean,
        default=True
    )

    activo = Column(
        Boolean,
        default=True
    )

    # ==========================
    # Auditoría
    # ==========================

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
            f"<Empresa("
            f"id={self.id}, "
            f"nit='{self.nit}', "
            f"razon_social='{self.razon_social}')>"
        )


class EmpresaBanco(Base):

    __tablename__ = "empresa_bancos"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    empresa_id = Column(
        Integer,
        ForeignKey("empresa.id"),
        nullable=False,
    )

    banco = Column(
        String(120),
        nullable=False,
    )

    tipo_cuenta = Column(
        String(30),
        default="Corriente",
    )

    numero_cuenta = Column(
        String(50),
        nullable=False,
    )

    titular = Column(
        String(200),
    )

    activo = Column(
        Boolean,
        default=True,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )