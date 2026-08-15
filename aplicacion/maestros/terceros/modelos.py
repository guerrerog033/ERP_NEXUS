from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
)
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class Tercero(Base):

    __tablename__ = "terceros"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # =====================================================
    # Clasificación
    # =====================================================

    tipo_tercero = Column(
        String(30),
        nullable=False,
    )

    es_cliente = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    es_proveedor = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    es_empleado = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    es_vendedor = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    tipo_documento = Column(
        String(10),
        nullable=False,
    )

    numero_documento = Column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
    )

    dv = Column(
        String(2)
    )

    # =====================================================
    # Persona / Empresa
    # =====================================================

    razon_social = Column(
        String(200)
    )

    nombre_comercial = Column(
        String(200)
    )

    primer_nombre = Column(
        String(100)
    )

    segundo_nombre = Column(
        String(100)
    )

    primer_apellido = Column(
        String(100)
    )

    segundo_apellido = Column(
        String(100)
    )

    # =====================================================
    # Ubicación
    # =====================================================

    direccion = Column(
        String(200)
    )

    ciudad = Column(
        String(100)
    )

    departamento = Column(
        String(100)
    )

    pais = Column(
        String(100)
    )

    # =====================================================
    # Contacto
    # =====================================================

    telefono = Column(
        String(30)
    )

    celular = Column(
        String(30)
    )

    correo = Column(
        String(150)
    )

    # =====================================================
    # Información tributaria
    # =====================================================

    tipo_regimen_iva = Column(
        String(80),
    )

    resp_o13 = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    resp_o15 = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    resp_o23 = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    resp_o47 = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    resp_r99_pn = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    retefuente_id = Column(
        Integer,
        ForeignKey("impuestos.id"),
    )

    reteica_id = Column(
        Integer,
        ForeignKey("impuestos.id"),
    )

    reteiva_id = Column(
        Integer,
        ForeignKey("impuestos.id"),
    )

    lista_precio_id = Column(
        Integer,
        ForeignKey("listas_precio.id"),
    )

    dias_credito = Column(
        Integer,
        nullable=False,
        default=0,
    )

    cupo_credito = Column(
        Float,
        nullable=False,
        default=0,
    )

    vendedor_asignado = Column(
        String(120),
    )

    vendedor_id = Column(
        Integer,
        ForeignKey("vendedores.id"),
    )

    forma_pago_id = Column(
        Integer,
        ForeignKey("formas_pago.id"),
    )

    # =====================================================
    # Portal de autoconsulta
    # =====================================================

    portal_token = Column(
        String(64),
        unique=True,
    )

    # =====================================================
    # Estado
    # =====================================================

    activo = Column(
        Boolean,
        nullable=False,
        default=True,
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

    # =====================================================
    # Propiedades
    # =====================================================

    @property
    def nombre_completo(self):

        if self.razon_social:

            return self.razon_social

        return " ".join(

            filter(

                None,

                [

                    self.primer_nombre,

                    self.segundo_nombre,

                    self.primer_apellido,

                    self.segundo_apellido,

                ],

            )

        )

    # =====================================================
    # Representación
    # =====================================================

    def __repr__(self):

        return (

            f"<Tercero("

            f"id={self.id}, "

            f"documento='{self.numero_documento}', "

            f"nombre='{self.nombre_completo}')>"

        )


class PerfilCliente(Base):

    __tablename__ = "perfiles_cliente"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    tercero_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        unique=True,
        nullable=False,
    )

    codigo_cliente = Column(
        String(30),
        unique=True,
    )

    zona = Column(
        String(80),
    )

    descuento = Column(
        Float,
        nullable=False,
        default=0,
    )

    estado_cartera = Column(
        String(30),
        default="activo",
    )

    observaciones = Column(
        String(500),
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class PerfilProveedor(Base):

    __tablename__ = "perfiles_proveedor"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    tercero_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        unique=True,
        nullable=False,
    )

    codigo_proveedor = Column(
        String(30),
        unique=True,
    )

    cuenta_contable = Column(
        String(30),
    )

    banco = Column(
        String(120),
    )

    cuenta_bancaria = Column(
        String(50),
    )

    condiciones_comerciales = Column(
        String(500),
    )

    observaciones = Column(
        String(500),
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class TerceroDireccion(Base):

    __tablename__ = "tercero_direcciones"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    tercero_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
    )

    etiqueta = Column(
        String(40),
        default="Principal",
    )

    direccion = Column(
        String(200),
    )

    ciudad = Column(
        String(100),
    )

    departamento = Column(
        String(100),
    )

    pais = Column(
        String(100),
    )

    principal = Column(
        Boolean,
        default=False,
        nullable=False,
    )


class TerceroContacto(Base):

    __tablename__ = "tercero_contactos"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    tercero_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
    )

    nombre = Column(
        String(120),
        nullable=False,
    )

    cargo = Column(
        String(80),
    )

    telefono = Column(
        String(30),
    )

    correo = Column(
        String(150),
    )

    principal = Column(
        Boolean,
        default=False,
        nullable=False,
    )


class TerceroCuentaBancaria(Base):

    __tablename__ = "tercero_cuentas_bancarias"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    tercero_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
    )

    banco = Column(
        String(120),
        nullable=False,
    )

    tipo_cuenta = Column(
        String(20),
        default="Ahorros",
        nullable=False,
    )

    numero_cuenta = Column(
        String(50),
        nullable=False,
    )

    titular = Column(
        String(200),
    )

    principal = Column(
        Boolean,
        default=False,
        nullable=False,
    )