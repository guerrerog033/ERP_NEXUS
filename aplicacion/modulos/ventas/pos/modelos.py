from __future__ import annotations

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from aplicacion.base_datos.tipos import DINERO
from aplicacion.base_datos.conexion import Base


class PosVentaLog(Base):
    """
    Trazabilidad de ventas POS (totales de caja).
    """

    __tablename__ = "pos_ventas_log"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    factura_id = Column(
        Integer,
        ForeignKey("facturas_venta.id"),
        nullable=False,
    )

    total = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    recibido = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    cambio = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    metodo_pago = Column(
        String(30),
        nullable=False,
        default="efectivo",
    )

    usuario = Column(
        String(50),
        nullable=False,
        default="sistema",
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class PosCierreCaja(Base):
    """
    Cierre diario de caja POS con arqueo de efectivo.
    """

    __tablename__ = "pos_cierres_caja"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    fecha = Column(
        Date,
        nullable=False,
    )

    usuario = Column(
        String(50),
        nullable=False,
        default="sistema",
    )

    efectivo_esperado = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    efectivo_contado = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    diferencia = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    total_ventas = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    ventas_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    observaciones = Column(
        Text,
    )

    fecha_cierre = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
