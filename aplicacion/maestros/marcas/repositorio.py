from sqlalchemy import or_

from aplicacion.comunes.repositorio_base import RepositorioBase
from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.marcas.modelos import Marca


class RepositorioMarca(RepositorioBase):

    modelo = Marca

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(Marca)
                .filter(
                    or_(
                        Marca.codigo.ilike(f"%{texto}%"),
                        Marca.nombre.ilike(f"%{texto}%"),
                        Marca.descripcion.ilike(f"%{texto}%")
                    )
                )
                .order_by(Marca.nombre)
                .all()
            )

        finally:

            db.close()

    @classmethod
    def existe_codigo(cls, codigo, excluir_id=None):

        db = SessionLocal()

        try:

            consulta = (
                db.query(Marca)
                .filter(
                    Marca.codigo == codigo
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Marca.id != excluir_id
                )

            return consulta.first() is not None

        finally:

            db.close()