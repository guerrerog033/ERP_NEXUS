from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import ProductoKitComponente


class ProductoKitComponenteRepositorio(RepositorioBase):

    modelo = ProductoKitComponente

    @classmethod
    def listar_por_kit(cls, kit_id: int) -> list:

        db = SessionLocal()

        try:

            return (
                db.query(ProductoKitComponente)
                .filter(
                    ProductoKitComponente.kit_id == kit_id,
                )
                .order_by(
                    ProductoKitComponente.id,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def existe_componente(
        cls,
        kit_id: int,
        componente_id: int,
        excluir_id: int | None = None,
    ) -> bool:

        db = SessionLocal()

        try:

            consulta = db.query(ProductoKitComponente).filter(
                ProductoKitComponente.kit_id == kit_id,
                ProductoKitComponente.componente_id == componente_id,
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    ProductoKitComponente.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()
