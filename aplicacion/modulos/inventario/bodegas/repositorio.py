from sqlalchemy import or_

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from aplicacion.modulos.inventario.modelos import Bodega


class RepositorioBodega(RepositorioBase):

    modelo = Bodega

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(Bodega)
                .filter(
                    or_(
                        Bodega.codigo.ilike(
                            f"%{texto}%",
                        ),
                        Bodega.nombre.ilike(
                            f"%{texto}%",
                        ),
                    ),
                )
                .order_by(Bodega.nombre)
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
                db.query(Bodega)
                .filter(
                    Bodega.codigo == codigo,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Bodega.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def obtener_activas(cls):

        db = SessionLocal()

        try:

            return (
                db.query(Bodega)
                .filter(
                    Bodega.activo.is_(True),
                )
                .order_by(Bodega.nombre)
                .all()
            )

        finally:

            db.close()
