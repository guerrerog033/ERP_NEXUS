from __future__ import annotations

from sqlalchemy import or_

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase
from aplicacion.modulos.contabilidad.modelos import PlanCuenta


class RepositorioPlanCuenta(RepositorioBase):

    modelo = PlanCuenta

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(PlanCuenta)
                .filter(
                    or_(
                        PlanCuenta.codigo.ilike(
                            f"%{texto}%",
                        ),
                        PlanCuenta.nombre.ilike(
                            f"%{texto}%",
                        ),
                    ),
                )
                .order_by(PlanCuenta.codigo)
                .all()
            )

        finally:

            db.close()

    @classmethod
    def existe_codigo(
        cls,
        codigo,
        excluir_id=None,
    ):

        db = SessionLocal()

        try:

            consulta = (
                db.query(PlanCuenta)
                .filter(
                    PlanCuenta.codigo == codigo,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    PlanCuenta.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def buscar_para_lookup(
        cls,
        texto: str,
        limite: int = 30,
    ):

        db = SessionLocal()

        try:

            consulta = db.query(PlanCuenta).filter(
                PlanCuenta.activo.is_(True),
            )

            if texto.strip():

                consulta = consulta.filter(
                    or_(
                        PlanCuenta.codigo.ilike(
                            f"%{texto.strip()}%",
                        ),
                        PlanCuenta.nombre.ilike(
                            f"%{texto.strip()}%",
                        ),
                    ),
                )

            return (
                consulta.order_by(
                    PlanCuenta.codigo,
                )
                .limit(limite)
                .all()
            )

        finally:

            db.close()
