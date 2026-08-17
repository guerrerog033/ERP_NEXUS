from __future__ import annotations

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
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base
from aplicacion.base_datos.tipos import CANTIDAD, DINERO


class FacturaRecurrente(Base):
    """
    Plantilla de facturación recurrente: genera una FacturaVenta
    real cada vez que se cumple su periodicidad (mensual,
    quincenal, trimestral o anual), típicamente para servicios o
    arriendos con cobro periódico fijo.
    """

    __tablename__ = "facturas_recurrentes"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nombre = Column(
        String(150),
        nullable=False,
    )

    cliente_id = Column(
        Integer,
        ForeignKey("terceros.id"),
        nullable=False,
    )

    periodicidad = Column(
        String(20),
        nullable=False,
        default="mensual",
    )

    proxima_fecha = Column(
        Date,
        nullable=False,
    )

    ultima_generada_en = Column(
        Date,
    )

    facturas_generadas = Column(
        Integer,
        nullable=False,
        default=0,
    )

    observaciones = Column(
        Text,
    )

    activa = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    detalles = relationship(
        "FacturaRecurrenteDetalle",
        back_populates="plantilla",
        cascade="all, delete-orphan",
        order_by="FacturaRecurrenteDetalle.orden",
    )

    def __repr__(self) -> str:

        return (
            f"<FacturaRecurrente("
            f"id={self.id}, "
            f"nombre='{self.nombre}', "
            f"periodicidad='{self.periodicidad}')>"
        )


class FacturaRecurrenteDetalle(Base):

    __tablename__ = "factura_recurrente_detalles"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    plantilla_id = Column(
        Integer,
        ForeignKey(
            "facturas_recurrentes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    producto_id = Column(
        Integer,
        ForeignKey("productos.id"),
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
        nullable=False,
        default=False,
    )

    orden = Column(
        Integer,
        nullable=False,
        default=0,
    )

    plantilla = relationship(
        "FacturaRecurrente",
        back_populates="detalles",
    )
