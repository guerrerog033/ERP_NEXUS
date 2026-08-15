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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base
from aplicacion.base_datos.tipos import (
    CANTIDAD,
    DINERO,
)


class Bodega(Base):

    __tablename__ = "bodegas"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    codigo = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    nombre = Column(
        String(150),
        nullable=False,
    )

    direccion = Column(
        String(200),
        nullable=True,
    )

    ciudad = Column(
        String(100),
        nullable=True,
    )

    responsable = Column(
        String(150),
        nullable=True,
    )

    activo = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    existencias = relationship(
        "ExistenciaBodega",
        back_populates="bodega",
        cascade="all, delete-orphan",
    )

    movimientos = relationship(
        "MovimientoInventario",
        back_populates="bodega",
    )


class ExistenciaBodega(Base):

    __tablename__ = "existencias_bodega"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    bodega_id = Column(
        Integer,
        ForeignKey(
            "bodegas.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    producto_id = Column(
        Integer,
        ForeignKey(
            "productos.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    producto_variante_id = Column(
        Integer,
        ForeignKey(
            "producto_variantes.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    cantidad = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    cantidad_reservada = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    bodega = relationship(
        "Bodega",
        back_populates="existencias",
    )

    producto = relationship(
        "Producto",
        back_populates="existencias_bodega",
    )

    variante = relationship(
        "ProductoVariante",
        back_populates="existencias_bodega",
    )

    @property
    def disponible(self):

        return (
            (self.cantidad or 0)
            - (self.cantidad_reservada or 0)
        )


class MovimientoInventario(Base):

    __tablename__ = "movimientos_inventario"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    bodega_id = Column(
        Integer,
        ForeignKey(
            "bodegas.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    producto_id = Column(
        Integer,
        ForeignKey(
            "productos.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    producto_variante_id = Column(
        Integer,
        ForeignKey(
            "producto_variantes.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    lote_serie_id = Column(
        Integer,
        ForeignKey(
            "lotes_series.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    tipo = Column(
        String(30),
        nullable=False,
        default="entrada",
    )

    cantidad = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    costo_unitario = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    referencia = Column(
        String(50),
        nullable=True,
    )

    referencia_id = Column(
        Integer,
        nullable=True,
    )

    fecha = Column(
        Date,
        nullable=False,
    )

    observaciones = Column(
        Text,
        nullable=True,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    bodega = relationship(
        "Bodega",
        back_populates="movimientos",
    )

    producto = relationship(
        "Producto",
    )

    variante = relationship(
        "ProductoVariante",
    )

    lote_serie = relationship(
        "LoteSerie",
    )


class LoteSerie(Base):
    """
    Un lote o número de serie de un producto (según
    Producto.maneja_lote / maneja_serie). La existencia real por
    bodega vive en ExistenciaLoteSerie — este modelo es solo la
    identidad del lote/serie (número, vencimiento si aplica).
    """

    __tablename__ = "lotes_series"

    __table_args__ = (
        UniqueConstraint(
            "producto_id",
            "numero",
            name="uq_producto_lote_serie_numero",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    producto_id = Column(
        Integer,
        ForeignKey(
            "productos.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    tipo = Column(
        String(10),
        nullable=False,
        default="lote",
    )

    numero = Column(
        String(60),
        nullable=False,
    )

    fecha_fabricacion = Column(
        Date,
        nullable=True,
    )

    fecha_vencimiento = Column(
        Date,
        nullable=True,
    )

    notas = Column(
        String(300),
        nullable=True,
    )

    activo = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    producto = relationship(
        "Producto",
    )

    existencias = relationship(
        "ExistenciaLoteSerie",
        back_populates="lote_serie",
        cascade="all, delete-orphan",
    )


class ExistenciaLoteSerie(Base):
    """
    Cantidad disponible de un lote/serie específico en una bodega.
    Para tipo="serie" la cantidad es conceptualmente 0 o 1 (una
    unidad física única) — no se fuerza a nivel de columna para no
    complicar el modelo, se valida en el servicio.
    """

    __tablename__ = "existencias_lote_serie"

    __table_args__ = (
        UniqueConstraint(
            "bodega_id",
            "lote_serie_id",
            name="uq_bodega_lote_serie",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    bodega_id = Column(
        Integer,
        ForeignKey(
            "bodegas.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    lote_serie_id = Column(
        Integer,
        ForeignKey(
            "lotes_series.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    cantidad = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    bodega = relationship(
        "Bodega",
    )

    lote_serie = relationship(
        "LoteSerie",
        back_populates="existencias",
    )
