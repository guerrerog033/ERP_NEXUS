from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import (
    ContratoEmpleado,
    Empleado,
    LiquidacionConcepto,
    LiquidacionNomina,
    NovedadNomina,
    PeriodoNomina,
    ProvisionPrestacion,
)


class RepositorioEmpleado(RepositorioBase):

    modelo = Empleado

    @classmethod
    def buscar(
        cls,
        texto: str,
    ):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(Empleado)
                .filter(
                    or_(
                        Empleado.codigo.ilike(
                            f"%{texto}%",
                        ),
                        Empleado.numero_documento.ilike(
                            f"%{texto}%",
                        ),
                        Empleado.primer_nombre.ilike(
                            f"%{texto}%",
                        ),
                        Empleado.primer_apellido.ilike(
                            f"%{texto}%",
                        ),
                        Empleado.cargo.ilike(
                            f"%{texto}%",
                        ),
                    ),
                )
                .order_by(
                    Empleado.primer_apellido,
                    Empleado.primer_nombre,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def existe_codigo(
        cls,
        codigo: str,
        excluir_id=None,
    ) -> bool:

        db = SessionLocal()

        try:

            consulta = (
                db.query(Empleado)
                .filter(
                    Empleado.codigo == codigo,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Empleado.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def existe_documento(
        cls,
        tipo_documento: str,
        numero_documento: str,
        excluir_id=None,
    ) -> bool:

        db = SessionLocal()

        try:

            consulta = (
                db.query(Empleado)
                .filter(
                    Empleado.tipo_documento
                    == tipo_documento,
                    Empleado.numero_documento
                    == numero_documento,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Empleado.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def listar_activos(cls):

        db = SessionLocal()

        try:

            return (
                db.query(Empleado)
                .filter(
                    Empleado.activo.is_(True),
                )
                .order_by(
                    Empleado.primer_apellido,
                    Empleado.primer_nombre,
                )
                .all()
            )

        finally:

            db.close()


class RepositorioContratoEmpleado(RepositorioBase):

    modelo = ContratoEmpleado

    @classmethod
    def obtener_todos(
        cls,
        ordenar_por=None,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(ContratoEmpleado)
                .options(
                    joinedload(
                        ContratoEmpleado.empleado,
                    ),
                )
                .order_by(
                    ContratoEmpleado.fecha_inicio.desc(),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def buscar(
        cls,
        texto: str,
    ):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(ContratoEmpleado)
                .options(
                    joinedload(
                        ContratoEmpleado.empleado,
                    ),
                )
                .join(Empleado)
                .filter(
                    or_(
                        Empleado.codigo.ilike(
                            f"%{texto}%",
                        ),
                        Empleado.numero_documento.ilike(
                            f"%{texto}%",
                        ),
                        Empleado.primer_nombre.ilike(
                            f"%{texto}%",
                        ),
                        Empleado.primer_apellido.ilike(
                            f"%{texto}%",
                        ),
                        ContratoEmpleado.cargo.ilike(
                            f"%{texto}%",
                        ),
                    ),
                )
                .order_by(
                    ContratoEmpleado.fecha_inicio.desc(),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def obtener_vigente(
        cls,
        empleado_id: int,
        *,
        anio: int,
        mes: int,
    ):

        db = SessionLocal()

        try:

            from datetime import date
            import calendar

            ultimo_dia = calendar.monthrange(
                anio,
                mes,
            )[1]

            fecha_ref = date(
                anio,
                mes,
                ultimo_dia,
            )

            return (
                db.query(ContratoEmpleado)
                .filter(
                    ContratoEmpleado.empleado_id
                    == empleado_id,
                    ContratoEmpleado.vigente.is_(
                        True,
                    ),
                    ContratoEmpleado.fecha_inicio
                    <= fecha_ref,
                    (
                        ContratoEmpleado.fecha_fin.is_(
                            None,
                        )
                        | (
                            ContratoEmpleado.fecha_fin
                            >= date(
                                anio,
                                mes,
                                1,
                            )
                        )
                    ),
                )
                .order_by(
                    ContratoEmpleado.fecha_inicio.desc(),
                )
                .first()
            )

        finally:

            db.close()


class RepositorioNovedadNomina(RepositorioBase):

    modelo = NovedadNomina

    @classmethod
    def obtener_todos(
        cls,
        ordenar_por=None,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(NovedadNomina)
                .options(
                    joinedload(
                        NovedadNomina.empleado,
                    ),
                    joinedload(
                        NovedadNomina.periodo,
                    ),
                )
                .order_by(
                    NovedadNomina.id.desc(),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def buscar(
        cls,
        texto: str,
    ):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(NovedadNomina)
                .options(
                    joinedload(
                        NovedadNomina.empleado,
                    ),
                    joinedload(
                        NovedadNomina.periodo,
                    ),
                )
                .join(Empleado)
                .filter(
                    or_(
                        Empleado.codigo.ilike(
                            f"%{texto}%",
                        ),
                        Empleado.numero_documento.ilike(
                            f"%{texto}%",
                        ),
                        NovedadNomina.tipo.ilike(
                            f"%{texto}%",
                        ),
                        NovedadNomina.observaciones.ilike(
                            f"%{texto}%",
                        ),
                    ),
                )
                .order_by(
                    NovedadNomina.id.desc(),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def listar_por_periodo_empleado(
        cls,
        periodo_id: int,
        empleado_id: int,
    ) -> list[NovedadNomina]:

        db = SessionLocal()

        try:

            return (
                db.query(NovedadNomina)
                .filter(
                    NovedadNomina.periodo_id
                    == periodo_id,
                    NovedadNomina.empleado_id
                    == empleado_id,
                )
                .order_by(
                    NovedadNomina.id,
                )
                .all()
            )

        finally:

            db.close()


class RepositorioProvisionPrestacion(RepositorioBase):

    modelo = ProvisionPrestacion

    @classmethod
    def eliminar_por_periodo(
        cls,
        periodo_id: int,
    ) -> None:

        db = SessionLocal()

        try:

            db.query(ProvisionPrestacion).filter(
                ProvisionPrestacion.periodo_id
                == periodo_id,
            ).delete()

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def listar_por_periodo(
        cls,
        periodo_id: int,
    ) -> list[ProvisionPrestacion]:

        db = SessionLocal()

        try:

            return (
                db.query(ProvisionPrestacion)
                .options(
                    joinedload(
                        ProvisionPrestacion.empleado,
                    ),
                )
                .filter(
                    ProvisionPrestacion.periodo_id
                    == periodo_id,
                )
                .order_by(
                    ProvisionPrestacion.empleado_id,
                    ProvisionPrestacion.tipo,
                )
                .all()
            )

        finally:

            db.close()


class RepositorioPeriodoNomina(RepositorioBase):

    modelo = PeriodoNomina

    @classmethod
    def obtener_por_anio_mes(
        cls,
        anio: int,
        mes: int,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(PeriodoNomina)
                .filter(
                    PeriodoNomina.anio == anio,
                    PeriodoNomina.mes == mes,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def obtener_por_id(
        cls,
        periodo_id: int,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(PeriodoNomina)
                .filter(
                    PeriodoNomina.id
                    == periodo_id,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def actualizar_integracion(
        cls,
        periodo_id: int,
        **campos,
    ):

        db = SessionLocal()

        try:

            periodo = (
                db.query(PeriodoNomina)
                .filter(
                    PeriodoNomina.id
                    == periodo_id,
                )
                .first()
            )

            if periodo is None:

                raise ValueError(
                    "Periodo no encontrado.",
                )

            for clave, valor in campos.items():

                setattr(
                    periodo,
                    clave,
                    valor,
                )

            db.commit()
            db.refresh(periodo)

            return periodo

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def listar_ordenados(cls):

        db = SessionLocal()

        try:

            return (
                db.query(PeriodoNomina)
                .order_by(
                    PeriodoNomina.anio.desc(),
                    PeriodoNomina.mes.desc(),
                )
                .all()
            )

        finally:

            db.close()


class RepositorioLiquidacionNomina(RepositorioBase):

    modelo = LiquidacionNomina

    @classmethod
    def listar_por_periodo(
        cls,
        periodo_id: int,
    ) -> list[LiquidacionNomina]:

        db = SessionLocal()

        try:

            return (
                db.query(LiquidacionNomina)
                .options(
                    joinedload(
                        LiquidacionNomina.empleado,
                    ),
                    joinedload(
                        LiquidacionNomina.conceptos,
                    ),
                )
                .filter(
                    LiquidacionNomina.periodo_id
                    == periodo_id,
                )
                .order_by(
                    LiquidacionNomina.id,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def eliminar_por_periodo(
        cls,
        periodo_id: int,
    ) -> None:

        db = SessionLocal()

        try:

            db.query(LiquidacionConcepto).filter(
                LiquidacionConcepto.liquidacion_id.in_(
                    db.query(
                        LiquidacionNomina.id,
                    ).filter(
                        LiquidacionNomina.periodo_id
                        == periodo_id,
                    ),
                ),
            ).delete(
                synchronize_session=False,
            )

            db.query(LiquidacionNomina).filter(
                LiquidacionNomina.periodo_id
                == periodo_id,
            ).delete()

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
