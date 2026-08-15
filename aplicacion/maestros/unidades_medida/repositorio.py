from sqlalchemy import or_

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import UnidadMedida


class UnidadMedidaRepositorio(RepositorioBase):

    modelo = UnidadMedida

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(UnidadMedida)
                .filter(
                    or_(
                        UnidadMedida.codigo.ilike(f"%{texto}%"),
                        UnidadMedida.nombre.ilike(f"%{texto}%"),
                    )
                )
                .order_by(UnidadMedida.nombre)
                .all()
            )

        finally:

            db.close()

    @classmethod
    def existe_codigo(cls, codigo, excluir_id=None):

        db = SessionLocal()

        try:

            consulta = db.query(UnidadMedida).filter(
                UnidadMedida.codigo == codigo
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    UnidadMedida.id != excluir_id
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def obtener_por_codigo(cls, codigo):

        db = SessionLocal()

        try:

            return (
                db.query(UnidadMedida)
                .filter(
                    UnidadMedida.codigo == codigo,
                )
                .first()
            )

        finally:

            db.close()
