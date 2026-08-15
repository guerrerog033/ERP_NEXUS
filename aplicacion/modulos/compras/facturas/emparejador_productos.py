from __future__ import annotations

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.productos.modelos import Producto, ProductoVariante


class EmparejadorProductosFactura:
    """Resuelve productos de líneas importadas desde XML."""

    @classmethod
    def emparejar_linea(
        cls,
        *,
        codigo: str = "",
        codigo_barras: str = "",
        referencia: str = "",
        descripcion: str = "",
    ) -> tuple[int | None, int | None]:
        db = SessionLocal()

        try:
            for valor in (
                codigo,
                codigo_barras,
                referencia,
            ):
                producto_id, variante_id = cls._buscar_por_codigo(
                    db,
                    valor,
                )

                if producto_id is not None:
                    return producto_id, variante_id

            if descripcion:
                return cls._buscar_por_descripcion(
                    db,
                    descripcion,
                )

            return None, None

        finally:
            db.close()

    @classmethod
    def _buscar_por_codigo(
        cls,
        db,
        codigo: str,
    ) -> tuple[int | None, int | None]:
        codigo = str(
            codigo or "",
        ).strip()

        if not codigo:
            return None, None

        variante = (
            db.query(ProductoVariante)
            .filter(
                ProductoVariante.codigo == codigo,
            )
            .first()
        )

        if variante is not None:
            return variante.producto_id, variante.id

        variante = (
            db.query(ProductoVariante)
            .filter(
                ProductoVariante.codigo_barras == codigo,
            )
            .first()
        )

        if variante is not None:
            return variante.producto_id, variante.id

        producto = (
            db.query(Producto)
            .filter(
                Producto.codigo == codigo,
            )
            .first()
        )

        if producto is not None:
            return producto.id, None

        producto = (
            db.query(Producto)
            .filter(
                Producto.codigo_barras == codigo,
            )
            .first()
        )

        if producto is not None:
            return producto.id, None

        return None, None

    @classmethod
    def _buscar_por_descripcion(
        cls,
        db,
        descripcion: str,
    ) -> tuple[int | None, int | None]:
        texto = str(
            descripcion or "",
        ).strip()

        if len(texto) < 4:
            return None, None

        producto = (
            db.query(Producto)
            .filter(
                Producto.nombre.ilike(
                    texto,
                ),
            )
            .first()
        )

        if producto is not None:
            return producto.id, None

        producto = (
            db.query(Producto)
            .filter(
                Producto.nombre.ilike(
                    f"%{texto[:40]}%",
                ),
            )
            .first()
        )

        if producto is not None:
            return producto.id, None

        return None, None
