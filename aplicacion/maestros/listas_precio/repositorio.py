from sqlalchemy import or_

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import ListaPrecio


class RepositorioListaPrecio(RepositorioBase):

    modelo = ListaPrecio

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(ListaPrecio)
                .filter(
                    or_(
                        ListaPrecio.codigo.ilike(
                            f"%{texto}%",
                        ),
                        ListaPrecio.nombre.ilike(
                            f"%{texto}%",
                        ),
                    )
                )
                .order_by(ListaPrecio.nombre)
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
                db.query(ListaPrecio)
                .filter(
                    ListaPrecio.codigo == codigo,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    ListaPrecio.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def obtener_predeterminada(cls):

        db = SessionLocal()

        try:

            return (
                db.query(ListaPrecio)
                .filter(
                    ListaPrecio.predeterminada.is_(True),
                    ListaPrecio.activo.is_(True),
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def contar(cls):

        return super().contar()
