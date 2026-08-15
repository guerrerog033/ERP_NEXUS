from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class Atributo(Base):

    __tablename__ = "atributos"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    codigo = Column(
        String(30),
        unique=True,
        nullable=False,
    )

    nombre = Column(
        String(80),
        nullable=False,
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

    valores = relationship(
        "ValorAtributo",
        back_populates="atributo",
        cascade="all, delete-orphan",
        order_by="ValorAtributo.orden",
    )


class ValorAtributo(Base):

    __tablename__ = "valores_atributo"

    __table_args__ = (
        UniqueConstraint(
            "atributo_id",
            "valor",
            name="uq_atributo_valor",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    atributo_id = Column(
        Integer,
        ForeignKey("atributos.id"),
        nullable=False,
    )

    valor = Column(
        String(80),
        nullable=False,
    )

    orden = Column(
        Integer,
        nullable=False,
        default=0,
    )

    activo = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    atributo = relationship(
        "Atributo",
        back_populates="valores",
    )
