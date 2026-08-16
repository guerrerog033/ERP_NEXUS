from __future__ import annotations

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from aplicacion.base_datos.conexion import Base
from aplicacion.base_datos.tipos import CANTIDAD, DINERO


class ProductoPrecioVolumen(Base):
    """
    Escalón de precio por volumen: a partir de ``cantidad_minima``
    unidades en una misma línea de documento, se aplica ``precio``
    en vez del precio base del producto (``Producto.precio_venta``).
    Independiente de las listas de precio (``ProductoPrecio``).
    """

    __tablename__ = "producto_precios_volumen"

    __table_args__ = (
        UniqueConstraint(
            "producto_id",
            "cantidad_minima",
            name="uq_producto_precio_volumen",
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

    cantidad_minima = Column(
        CANTIDAD,
        nullable=False,
    )

    precio = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    producto = relationship(
        "Producto",
        back_populates="precios_volumen",
    )

    def __repr__(self) -> str:

        return (
            f"<ProductoPrecioVolumen("
            f"id={self.id}, "
            f"producto_id={self.producto_id}, "
            f"cantidad_minima={self.cantidad_minima}, "
            f"precio={self.precio})>"
        )
