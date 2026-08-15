from __future__ import annotations

from sqlalchemy import or_

from aplicacion.autenticacion.modelos import Rol
from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase


class RepositorioRol(RepositorioBase):

    modelo = Rol

    @classmethod
    def obtener_todos(
        cls,
        ordenar_por=None,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(Rol)
                .order_by(
                    Rol.nombre,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def buscar(
        cls,
        texto,
    ):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(Rol)
                .filter(
                    or_(
                        Rol.codigo.ilike(
                            f"%{texto}%",
                        ),
                        Rol.nombre.ilike(
                            f"%{texto}%",
                        ),
                    ),
                )
                .order_by(
                    Rol.nombre,
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
                db.query(Rol)
                .filter(
                    Rol.codigo == codigo,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Rol.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()
