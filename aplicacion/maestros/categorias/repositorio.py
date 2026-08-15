from sqlalchemy import or_

from aplicacion.comunes.repositorio_base import RepositorioBase
from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.categorias.modelos import Categoria


class RepositorioCategoria(RepositorioBase):

    modelo = Categoria

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(Categoria)
                .filter(
                    or_(
                        Categoria.codigo.ilike(f"%{texto}%"),
                        Categoria.nombre.ilike(f"%{texto}%"),
                        Categoria.descripcion.ilike(f"%{texto}%")
                    )
                )
                .order_by(Categoria.nombre)
                .all()
            )

        finally:

            db.close()

    @classmethod
    def existe_codigo(cls, codigo, excluir_id=None):

        db = SessionLocal()

        try:

            consulta = (
                db.query(Categoria)
                .filter(
                    Categoria.codigo == codigo
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Categoria.id != excluir_id
                )

            return consulta.first() is not None

        finally:

            db.close()