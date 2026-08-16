from __future__ import annotations

from aplicacion.comunes.repositorio_base import RepositorioBase

from .precio_volumen_modelo import ProductoPrecioVolumen


class ProductoPrecioVolumenRepositorio(RepositorioBase):

    modelo = ProductoPrecioVolumen

    @classmethod
    def listar_por_producto(
        cls,
        producto_id: int,
    ) -> list:

        db = cls.obtener_sesion()

        try:

            return (
                db.query(cls.modelo)
                .filter(
                    cls.modelo.producto_id == producto_id,
                )
                .order_by(
                    cls.modelo.cantidad_minima,
                )
                .all()
            )

        finally:

            db.close()
