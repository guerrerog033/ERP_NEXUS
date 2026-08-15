from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.seguridad.modelos import AuditoriaEvento


class RepositorioAuditoria:

    @classmethod
    def listar(
        cls,
        *,
        limite: int = 500,
        usuario: str = "",
        accion: str = "",
        texto: str = "",
    ):

        db = SessionLocal()

        try:

            consulta = db.query(
                AuditoriaEvento,
            )

            if usuario.strip():

                consulta = consulta.filter(
                    AuditoriaEvento.usuario.ilike(
                        f"%{usuario.strip()}%",
                    ),
                )

            if accion.strip():

                consulta = consulta.filter(
                    AuditoriaEvento.accion.ilike(
                        f"%{accion.strip()}%",
                    ),
                )

            if texto.strip():

                consulta = consulta.filter(
                    or_(
                        AuditoriaEvento.detalle.ilike(
                            f"%{texto.strip()}%",
                        ),
                        AuditoriaEvento.entidad.ilike(
                            f"%{texto.strip()}%",
                        ),
                        AuditoriaEvento.modulo.ilike(
                            f"%{texto.strip()}%",
                        ),
                    ),
                )

            return (
                consulta.order_by(
                    AuditoriaEvento.fecha.desc(),
                    AuditoriaEvento.id.desc(),
                )
                .limit(
                    max(
                        1,
                        min(
                            limite,
                            2000,
                        ),
                    ),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def contar(cls) -> int:

        db = SessionLocal()

        try:

            return db.query(
                AuditoriaEvento,
            ).count()

        finally:

            db.close()
