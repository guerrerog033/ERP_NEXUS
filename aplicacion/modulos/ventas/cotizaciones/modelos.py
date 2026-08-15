from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from aplicacion.base_datos.tipos import (
    CANTIDAD,
    DINERO,
    PORCENTAJE,
)

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class Cotizacion(Base):

    __tablename__ = "cotizaciones"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    numero = Column(
        String(30),
        unique=True,
        nullable=False,
    )

    fecha = Column(
        Date,
        nullable=False,
    )

    cliente_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
    )

    formato_impresion = Column(
        String(20),
        nullable=False,
        default="carta",
    )

    observaciones = Column(
        Text,
    )

    vendedor = Column(
        String(120),
    )

    subtotal = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    total = Column(
        DINERO,
        nullable=False,
        default=0,
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

    estado = Column(
        String(20),
        nullable=False,
        default="borrador",
    )

    fecha_vigencia = Column(
        Date,
    )

    descuento_porcentaje = Column(
        PORCENTAJE,
        default=0,
    )

    descuento_valor = Column(
        DINERO,
        default=0,
    )

    condiciones_comerciales = Column(
        Text,
    )

    lista_precio_id = Column(
        Integer,
        ForeignKey("listas_precio.id"),
    )

    codigo_aceptacion = Column(
        String(20),
        unique=True,
    )

    codigo_verificacion = Column(
        String(20),
    )

    estado_aceptacion = Column(
        String(20),
        default="pendiente",
    )

    firma_cliente = Column(
        String(200),
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

    detalles = relationship(
        "CotizacionDetalle",
        back_populates="cotizacion",
        cascade="all, delete-orphan",
        order_by="CotizacionDetalle.orden",
    )

    def __repr__(self):

        return (
            f"<Cotizacion("
            f"id={self.id}, "
            f"numero='{self.numero}')>"
        )


class CotizacionDetalle(Base):

    __tablename__ = "cotizacion_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    cotizacion_id = Column(
        Integer,
        ForeignKey("cotizaciones.id"),
        nullable=False,
    )

    producto_id = Column(
        Integer,
        ForeignKey("productos.id"),
    )

    producto_variante_id = Column(
        Integer,
        ForeignKey("producto_variantes.id"),
    )

    descripcion = Column(
        String(250),
        nullable=False,
    )

    cantidad = Column(
        CANTIDAD,
        nullable=False,
        default=1,
    )

    precio_unitario = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    impuesto_id = Column(
        Integer,
        ForeignKey("impuestos.id"),
    )

    precio_incluye_iva = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    retefuente_id = Column(
        Integer,
        ForeignKey("impuestos.id"),
    )

    reteica_id = Column(
        Integer,
        ForeignKey("impuestos.id"),
    )

    descuento_porcentaje = Column(
        PORCENTAJE,
        default=0,
    )

    descuento_valor = Column(
        DINERO,
        default=0,
    )

    ficha_tecnica = Column(
        Text,
    )

    total_linea = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    orden = Column(
        Integer,
        nullable=False,
        default=0,
    )

    cotizacion = relationship(
        "Cotizacion",
        back_populates="detalles",
    )

    def __repr__(self):

        return (
            f"<CotizacionDetalle("
            f"id={self.id}, "
            f"descripcion='{self.descripcion}')>"
        )
