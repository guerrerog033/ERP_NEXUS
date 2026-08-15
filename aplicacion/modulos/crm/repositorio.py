from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import (
    ActividadCRM,
    OportunidadCRM,
)


class RepositorioOportunidadCRM(RepositorioBase):

    modelo = OportunidadCRM

    @classmethod
    def buscar(
        cls,
        texto: str,
    ):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(OportunidadCRM)
                .options(
                    joinedload(
                        OportunidadCRM.cliente,
                    ),
                )
                .filter(
                    or_(
                        OportunidadCRM.codigo.ilike(
                            f"%{texto}%",
                        ),
                        OportunidadCRM.titulo.ilike(
                            f"%{texto}%",
                        ),
                        OportunidadCRM.etapa.ilike(
                            f"%{texto}%",
                        ),
                    ),
                )
                .order_by(
                    OportunidadCRM.id.desc(),
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
                db.query(OportunidadCRM)
                .filter(
                    OportunidadCRM.codigo == codigo,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    OportunidadCRM.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def resumen(cls) -> dict[str, float | int]:

        db = SessionLocal()

        try:

            oportunidades = (
                db.query(OportunidadCRM)
                .filter(
                    OportunidadCRM.activo.is_(True),
                    OportunidadCRM.etapa.notin_(
                        [
                            "ganada",
                            "perdida",
                        ],
                    ),
                )
                .all()
            )

            return {
                "abiertas": len(oportunidades),
                "valor_pipeline": sum(
                    float(
                        item.valor_estimado or 0,
                    )
                    * float(
                        item.probabilidad or 0,
                    )
                    / 100
                    for item in oportunidades
                ),
            }

        finally:

            db.close()


class RepositorioActividadCRM(RepositorioBase):

    modelo = ActividadCRM

    @classmethod
    def obtener_todos(
        cls,
        ordenar_por=None,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(ActividadCRM)
                .options(
                    joinedload(
                        ActividadCRM.oportunidad,
                    ),
                )
                .order_by(
                    ActividadCRM.fecha.desc(),
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
                db.query(ActividadCRM)
                .options(
                    joinedload(
                        ActividadCRM.oportunidad,
                    ),
                )
                .filter(
                    or_(
                        ActividadCRM.titulo.ilike(
                            f"%{texto}%",
                        ),
                        ActividadCRM.tipo.ilike(
                            f"%{texto}%",
                        ),
                        ActividadCRM.descripcion.ilike(
                            f"%{texto}%",
                        ),
                    ),
                )
                .order_by(
                    ActividadCRM.fecha.desc(),
                )
                .all()
            )

        finally:

            db.close()
