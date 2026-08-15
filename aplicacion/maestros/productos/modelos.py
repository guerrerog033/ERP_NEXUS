from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base
from aplicacion.base_datos.tipos import (
    CANTIDAD,
    DINERO,
)


class Producto(Base):

    __tablename__ = "productos"

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

    codigo_barras = Column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
    )

    nombre = Column(
        String(200),
        nullable=False,
    )

    descripcion = Column(
        Text,
        nullable=True,
    )

    tipo = Column(
        String(20),
        nullable=False,
        default="producto",
    )

    unidad_medida_legacy = Column(
        "unidad_medida",
        String(20),
        nullable=True,
    )

    unidad_medida_id = Column(
        Integer,
        ForeignKey(
            "unidades_medida.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    categoria_id = Column(
        Integer,
        ForeignKey(
            "categorias.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    marca_id = Column(
        Integer,
        ForeignKey(
            "marcas.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    precio_venta = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    precio_incluye_iva = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    costo = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    # Referencia sincronizada desde ExistenciaBodega (kardex).
    existencia = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    stock_minimo = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    impuesto_venta_id = Column(
        Integer,
        ForeignKey(
            "impuestos.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    impuesto_compra_id = Column(
        Integer,
        ForeignKey(
            "impuestos.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    imagen = Column(
        String(500),
        nullable=True,
    )

    maneja_variantes = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    atributos_variante = Column(
        JSONB,
        nullable=True,
    )

    es_kit = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    maneja_lote = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    maneja_serie = Column(
        Boolean,
        nullable=False,
        default=False,
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

    fecha_actualizacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    unidad_medida = relationship(
        "UnidadMedida",
    )

    categoria = relationship(
        "Categoria",
    )

    marca = relationship(
        "Marca",
    )

    impuesto_venta = relationship(
        "Impuesto",
        foreign_keys=[impuesto_venta_id],
    )

    impuesto_compra = relationship(
        "Impuesto",
        foreign_keys=[impuesto_compra_id],
    )

    precios = relationship(
        "ProductoPrecio",
        back_populates="producto",
        cascade="all, delete-orphan",
        order_by="ProductoPrecio.id",
    )

    variantes = relationship(
        "ProductoVariante",
        back_populates="producto",
        cascade="all, delete-orphan",
        order_by="ProductoVariante.orden",
    )

    existencias_bodega = relationship(
        "ExistenciaBodega",
        back_populates="producto",
        viewonly=True,
    )

    @property
    def tiene_variantes(self) -> bool:

        return bool(
            self.maneja_variantes,
        )

    @property
    def unidad_medida_codigo(self) -> str:
        """
        Código de la unidad de medida por su id (no navega la
        relación ``unidad_medida``: el objeto suele venir de una
        sesión ya cerrada — ver aplicacion.comunes.repositorio_base
        — y la carga perezosa fallaría con DetachedInstanceError).
        """

        if not self.unidad_medida_id:

            return ""

        from aplicacion.maestros.unidades_medida.repositorio import (
            UnidadMedidaRepositorio,
        )

        unidad = UnidadMedidaRepositorio.obtener_por_id(
            self.unidad_medida_id,
        )

        return unidad.codigo if unidad is not None else ""

    def __repr__(self) -> str:

        return (
            f"<Producto("
            f"id={self.id}, "
            f"codigo='{self.codigo}', "
            f"nombre='{self.nombre}')>"
        )


class ProductoVariante(Base):

    __tablename__ = "producto_variantes"

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

    codigo = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    codigo_barras = Column(
        String(50),
        nullable=True,
        unique=True,
        index=True,
    )

    talla = Column(
        String(50),
        nullable=True,
    )

    color = Column(
        String(50),
        nullable=True,
    )

    calibre = Column(
        String(50),
        nullable=True,
    )

    largo = Column(
        String(50),
        nullable=True,
    )

    atributos = Column(
        JSONB,
        nullable=True,
    )

    precio_venta = Column(
        DINERO,
        nullable=True,
    )

    costo = Column(
        DINERO,
        nullable=True,
    )

    precio_incluye_iva = Column(
        Boolean,
        nullable=True,
    )

    impuesto_venta_id = Column(
        Integer,
        ForeignKey(
            "impuestos.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    impuesto_compra_id = Column(
        Integer,
        ForeignKey(
            "impuestos.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    imagen = Column(
        String(500),
        nullable=True,
    )

    # Referencia sincronizada desde ExistenciaBodega (kardex).
    existencia = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    activo = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    orden = Column(
        Integer,
        nullable=False,
        default=0,
    )

    producto = relationship(
        "Producto",
        back_populates="variantes",
    )

    impuesto_venta = relationship(
        "Impuesto",
        foreign_keys=[impuesto_venta_id],
    )

    impuesto_compra = relationship(
        "Impuesto",
        foreign_keys=[impuesto_compra_id],
    )

    existencias_bodega = relationship(
        "ExistenciaBodega",
        back_populates="variante",
        viewonly=True,
    )

    @property
    def nombre_completo(self) -> str:

        valores: list[str] = []

        if self.talla:

            valores.append(
                f"Talla: {self.talla}",
            )

        if self.color:

            valores.append(
                f"Color: {self.color}",
            )

        if self.calibre:

            valores.append(
                f"Calibre: {self.calibre}",
            )

        if self.largo:

            valores.append(
                f"Largo: {self.largo}",
            )

        if self.atributos:

            for nombre, valor in self.atributos.items():

                valores.append(
                    f"{nombre}: {valor}",
                )

        if not valores:

            return self.producto.nombre

        return (
            f"{self.producto.nombre} - "
            + ", ".join(valores)
        )

    def __repr__(self) -> str:

        return (
            f"<ProductoVariante("
            f"id={self.id}, "
            f"codigo='{self.codigo}', "
            f"producto_id={self.producto_id})>"
        )


class CatalogoVariante(Base):

    __tablename__ = "catalogo_variantes"

    __table_args__ = (
        UniqueConstraint(
            "tipo",
            "nombre_tipo",
            "valor",
            name="uq_catalogo_variante_valor",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    tipo = Column(
        String(30),
        nullable=False,
    )

    nombre_tipo = Column(
        String(60),
        nullable=False,
        default="",
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
        nullable=False,
        default=True,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class ProductoKitComponente(Base):
    """
    Componente de un kit/combo: un producto marcado como
    ``es_kit=True`` no tiene existencia propia, se compone de
    otros productos en las cantidades aquí definidas. No se
    permiten kits anidados (un componente no puede ser a su vez
    un kit) — se valida en el servicio, no aquí.
    """

    __tablename__ = "producto_kit_componentes"

    __table_args__ = (
        UniqueConstraint(
            "kit_id",
            "componente_id",
            name="uq_kit_componente",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    kit_id = Column(
        Integer,
        ForeignKey(
            "productos.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    componente_id = Column(
        Integer,
        ForeignKey(
            "productos.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    cantidad = Column(
        CANTIDAD,
        nullable=False,
        default=1,
    )

    kit = relationship(
        "Producto",
        foreign_keys=[kit_id],
    )

    componente = relationship(
        "Producto",
        foreign_keys=[componente_id],
    )


from .precio_modelo import ProductoPrecio  # noqa: E402,F401
