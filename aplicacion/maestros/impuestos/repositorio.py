from sqlalchemy import or_

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import Impuesto


class RepositorioImpuesto(RepositorioBase):

    modelo = Impuesto

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(Impuesto)
                .filter(
                    or_(
                        Impuesto.codigo.ilike(
                            f"%{texto}%",
                        ),
                        Impuesto.nombre.ilike(
                            f"%{texto}%",
                        ),
                    )
                )
                .order_by(Impuesto.nombre)
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
                db.query(Impuesto)
                .filter(
                    Impuesto.codigo == codigo,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Impuesto.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def contar(cls):

        return super().contar()

    @classmethod
    def obtener_por_codigo(
        cls,
        codigo: str,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(
                    Impuesto,
                )
                .filter(
                    Impuesto.codigo
                    == str(
                        codigo,
                    ).strip().upper(),
                )
                .first()
            )

        finally:

            db.close()
