from __future__ import annotations

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from aplicacion.base_datos.conexion import Base
from aplicacion.base_datos.tipos import DINERO


class ProductoPrecio(Base):

    __tablename__ = "producto_precios"

    __table_args__ = (
        UniqueConstraint(
            "producto_id",
            "lista_precio_id",
            name="uq_producto_lista_precio",
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

    lista_precio_id = Column(
        Integer,
        ForeignKey(
            "listas_precio.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    precio = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    impuesto_id = Column(
        Integer,
        ForeignKey(
            "impuestos.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    producto = relationship(
        "Producto",
        back_populates="precios",
    )

    lista_precio = relationship(
        "ListaPrecio",
    )

    impuesto = relationship(
        "Impuesto",
    )

    def __repr__(self) -> str:

        return (
            f"<ProductoPrecio("
            f"id={self.id}, "
            f"producto_id={self.producto_id}, "
            f"lista_precio_id={self.lista_precio_id}, "
            f"precio={self.precio})>"
        )
