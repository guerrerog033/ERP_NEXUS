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

from aplicacion.base_datos.tipos import (
    CANTIDAD,
    DINERO,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from aplicacion.base_datos.conexion import Base


class Empleado(Base):

    __tablename__ = "nomina_empleados"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    codigo = Column(
        String(20),
        unique=True,
        nullable=False,
    )

    tipo_documento = Column(
        String(20),
        nullable=False,
        default="CC",
    )

    numero_documento = Column(
        String(30),
        nullable=False,
    )

    dv = Column(
        String(2),
    )

    primer_nombre = Column(
        String(100),
        nullable=False,
    )

    segundo_nombre = Column(
        String(100),
    )

    primer_apellido = Column(
        String(100),
        nullable=False,
    )

    segundo_apellido = Column(
        String(100),
    )

    email = Column(
        String(120),
    )

    telefono = Column(
        String(30),
    )

    cargo = Column(
        String(120),
    )

    area = Column(
        String(120),
    )

    tipo_contrato = Column(
        String(30),
        nullable=False,
        default="indefinido",
    )

    salario_basico = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    fecha_ingreso = Column(
        Date,
    )

    eps = Column(
        String(120),
    )

    afp = Column(
        String(120),
    )

    arl = Column(
        String(120),
    )

    eps_codigo = Column(
        String(6),
    )

    afp_codigo = Column(
        String(6),
    )

    arl_codigo = Column(
        String(6),
    )

    auxilio_transporte = Column(
        DINERO,
        default=0,
    )

    salario_integral = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    clase_riesgo = Column(
        String(1),
        default="1",
    )

    centro_trabajo = Column(
        String(9),
        default="000000001",
    )

    departamento_codigo = Column(
        String(2),
        default="11",
    )

    municipio_codigo = Column(
        String(3),
        default="001",
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

    liquidaciones = relationship(
        "LiquidacionNomina",
        back_populates="empleado",
    )

    contratos = relationship(
        "ContratoEmpleado",
        back_populates="empleado",
    )

    novedades = relationship(
        "NovedadNomina",
        back_populates="empleado",
    )

    provisiones = relationship(
        "ProvisionPrestacion",
        back_populates="empleado",
    )

    @property
    def nombre_completo(self) -> str:

        partes = [
            self.primer_nombre,
            self.segundo_nombre,
            self.primer_apellido,
            self.segundo_apellido,
        ]

        return " ".join(
            parte.strip()
            for parte in partes
            if parte and str(parte).strip()
        )


class PeriodoNomina(Base):

    __tablename__ = "nomina_periodos"

    __table_args__ = (
        UniqueConstraint(
            "anio",
            "mes",
            name="uq_nomina_periodo_anio_mes",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    anio = Column(
        Integer,
        nullable=False,
    )

    mes = Column(
        Integer,
        nullable=False,
    )

    estado = Column(
        String(20),
        nullable=False,
        default="abierto",
    )

    observaciones = Column(
        Text,
    )

    fecha_liquidacion = Column(
        DateTime(timezone=True),
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    contabilizado = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    asiento_id = Column(
        Integer,
    )

    estado_dian = Column(
        String(30),
        default="pendiente",
    )

    cune = Column(
        String(120),
    )

    ruta_xml = Column(
        String(500),
    )

    ruta_pila = Column(
        String(500),
    )

    mensaje_dian = Column(
        Text,
    )

    ruta_zip = Column(
        String(500),
    )

    liquidaciones = relationship(
        "LiquidacionNomina",
        back_populates="periodo",
        cascade="all, delete-orphan",
    )

    novedades = relationship(
        "NovedadNomina",
        back_populates="periodo",
        cascade="all, delete-orphan",
    )

    provisiones = relationship(
        "ProvisionPrestacion",
        back_populates="periodo",
        cascade="all, delete-orphan",
    )

    @property
    def nombre(self) -> str:

        return f"{self.mes:02d}/{self.anio}"


class LiquidacionNomina(Base):

    __tablename__ = "nomina_liquidaciones"

    __table_args__ = (
        UniqueConstraint(
            "periodo_id",
            "empleado_id",
            name="uq_nomina_liquidacion_periodo_empleado",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    periodo_id = Column(
        Integer,
        ForeignKey("nomina_periodos.id"),
        nullable=False,
    )

    empleado_id = Column(
        Integer,
        ForeignKey("nomina_empleados.id"),
        nullable=False,
    )

    dias_trabajados = Column(
        Integer,
        nullable=False,
        default=30,
    )

    total_devengado = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    total_deducciones = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    neto_pagar = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    total_aportes_patronales = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    periodo = relationship(
        "PeriodoNomina",
        back_populates="liquidaciones",
    )

    empleado = relationship(
        "Empleado",
        back_populates="liquidaciones",
    )

    conceptos = relationship(
        "LiquidacionConcepto",
        back_populates="liquidacion",
        cascade="all, delete-orphan",
        order_by="LiquidacionConcepto.orden",
    )


class LiquidacionConcepto(Base):

    __tablename__ = "nomina_liquidacion_conceptos"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    liquidacion_id = Column(
        Integer,
        ForeignKey("nomina_liquidaciones.id"),
        nullable=False,
    )

    codigo = Column(
        String(20),
        nullable=False,
    )

    nombre = Column(
        String(120),
        nullable=False,
    )

    naturaleza = Column(
        String(30),
        nullable=False,
    )

    valor = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    orden = Column(
        Integer,
        nullable=False,
        default=0,
    )

    liquidacion = relationship(
        "LiquidacionNomina",
        back_populates="conceptos",
    )


class ContratoEmpleado(Base):

    __tablename__ = "nomina_contratos"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    empleado_id = Column(
        Integer,
        ForeignKey("nomina_empleados.id"),
        nullable=False,
    )

    fecha_inicio = Column(
        Date,
        nullable=False,
    )

    fecha_fin = Column(
        Date,
    )

    salario = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    tipo_contrato = Column(
        String(30),
        nullable=False,
        default="indefinido",
    )

    cargo = Column(
        String(120),
    )

    observaciones = Column(
        Text,
    )

    vigente = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    empleado = relationship(
        "Empleado",
        back_populates="contratos",
    )

    @property
    def empleado_nombre(self) -> str:

        if self.empleado is None:

            return ""

        return self.empleado.nombre_completo


class NovedadNomina(Base):

    __tablename__ = "nomina_novedades"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    periodo_id = Column(
        Integer,
        ForeignKey("nomina_periodos.id"),
        nullable=False,
    )

    empleado_id = Column(
        Integer,
        ForeignKey("nomina_empleados.id"),
        nullable=False,
    )

    tipo = Column(
        String(30),
        nullable=False,
    )

    cantidad = Column(
        CANTIDAD,
        nullable=False,
        default=0,
    )

    valor = Column(
        DINERO,
        default=0,
    )

    observaciones = Column(
        Text,
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    periodo = relationship(
        "PeriodoNomina",
        back_populates="novedades",
    )

    empleado = relationship(
        "Empleado",
        back_populates="novedades",
    )

    @property
    def empleado_nombre(self) -> str:

        if self.empleado is None:

            return ""

        return self.empleado.nombre_completo

    @property
    def periodo_nombre(self) -> str:

        if self.periodo is None:

            return ""

        return f"{self.periodo.mes:02d}/{self.periodo.anio}"


class ProvisionPrestacion(Base):

    __tablename__ = "nomina_provisiones"

    __table_args__ = (
        UniqueConstraint(
            "periodo_id",
            "empleado_id",
            "tipo",
            name="uq_nomina_provision_periodo_empleado_tipo",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    periodo_id = Column(
        Integer,
        ForeignKey("nomina_periodos.id"),
        nullable=False,
    )

    empleado_id = Column(
        Integer,
        ForeignKey("nomina_empleados.id"),
        nullable=False,
    )

    tipo = Column(
        String(30),
        nullable=False,
    )

    base = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    valor = Column(
        DINERO,
        nullable=False,
        default=0,
    )

    estado = Column(
        String(20),
        nullable=False,
        default="provisionado",
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    periodo = relationship(
        "PeriodoNomina",
        back_populates="provisiones",
    )

    empleado = relationship(
        "Empleado",
        back_populates="provisiones",
    )

    @property
    def empleado_nombre(self) -> str:

        if self.empleado is None:

            return ""

        return self.empleado.nombre_completo

    @property
    def periodo_nombre(self) -> str:

        if self.periodo is None:

            return ""

        return f"{self.periodo.mes:02d}/{self.periodo.anio}"
