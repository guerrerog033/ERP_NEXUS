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
from sqlalchemy.sql import func

from aplicacion.base_datos.tipos import (
    COORDENADA,
    DINERO,
)
from aplicacion.base_datos.conexion import Base


class DespachoPedido(Base):

    __tablename__ = "despachos_pedido"

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, nullable=False)
    remision_id = Column(
        Integer,
        ForeignKey("remisiones_venta.id"),
    )
    numero = Column(String(30), unique=True, nullable=False)
    estado = Column(String(30), default="en_preparacion")
    direccion = Column(String(250))
    ciudad = Column(String(80))
    departamento = Column(String(80))
    latitud = Column(COORDENADA)
    longitud = Column(COORDENADA)
    fecha_programada = Column(Date)
    hora_programada = Column(String(10))
    ventana_horaria = Column(String(40))
    receptor_nombre = Column(String(120))
    receptor_documento = Column(String(30))
    receptor_telefono = Column(String(30))
    prioridad = Column(String(20), default="normal")
    vehiculo = Column(String(80))
    conductor = Column(String(120))
    transportadora = Column(String(120))
    guia_numero = Column(String(60))
    costo_flete = Column(DINERO, default=0)
    observaciones = Column(Text)
    firma_cliente = Column(Text)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class DespachoEvidencia(Base):

    __tablename__ = "despacho_evidencias"

    id = Column(Integer, primary_key=True)
    despacho_id = Column(
        Integer,
        ForeignKey("despachos_pedido.id"),
        nullable=False,
    )
    tipo = Column(String(30), default="foto")
    ruta = Column(String(500))
    observaciones = Column(Text)
    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
