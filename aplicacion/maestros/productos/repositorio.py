from sqlalchemy import String, cast, or_
from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import Producto, ProductoPrecio, ProductoVariante


class RepositorioProducto(RepositorioBase):

    modelo = Producto

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(Producto)
                .filter(
                    or_(
                        Producto.codigo.ilike(
                            f"%{texto}%",
                        ),
                        Producto.codigo_barras.ilike(
                            f"%{texto}%",
                        ),
                        Producto.nombre.ilike(
                            f"%{texto}%",
                        ),
                        Producto.descripcion.ilike(
                            f"%{texto}%",
                        ),
                    )
                )
                .order_by(Producto.nombre)
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
                db.query(Producto)
                .filter(
                    Producto.codigo == codigo,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Producto.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def existe_codigo_barras(
        cls,
        codigo_barras,
        excluir_id=None,
    ):

        if not codigo_barras:

            return False

        db = SessionLocal()

        try:

            consulta = (
                db.query(Producto)
                .filter(
                    Producto.codigo_barras
                    == codigo_barras,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Producto.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def siguiente_secuencia(
        cls,
        prefijo: str,
    ) -> int:

        db = SessionLocal()

        try:

            codigos = (
                db.query(Producto.codigo)
                .filter(
                    Producto.codigo.like(
                        f"{prefijo}%",
                    )
                )
                .all()
            )

            maximo = 0

            for (codigo,) in codigos:

                sufijo = codigo[len(prefijo):]

                if sufijo.isdigit():

                    maximo = max(
                        maximo,
                        int(sufijo),
                    )

            return maximo + 1

        finally:

            db.close()

    @classmethod
    def obtener_completo(
        cls,
        id_registro,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(Producto)
                .options(
                    joinedload(
                        Producto.precios,
                    ),
                    joinedload(
                        Producto.variantes,
                    ),
                )
                .filter(
                    Producto.id == id_registro,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def guardar_precios(
        cls,
        producto_id,
        precios: list[dict],
    ):

        db = SessionLocal()

        try:

            (
                db.query(ProductoPrecio)
                .filter(
                    ProductoPrecio.producto_id
                    == producto_id,
                )
                .delete()
            )

            for item in precios:

                registro = ProductoPrecio(
                    producto_id=producto_id,
                    lista_precio_id=item[
                        "lista_precio_id"
                    ],
                    precio=item[
                        "precio"
                    ],
                    impuesto_id=item.get(
                        "impuesto_id",
                    ),
                )

                db.add(registro)

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def guardar_completo(
        cls,
        datos: dict,
        precios: list[dict],
    ):

        registro = cls.guardar(datos)

        cls.guardar_precios(
            registro.id,
            precios,
        )

        return cls.obtener_completo(
            registro.id,
        )

    @classmethod
    def actualizar_completo(
        cls,
        id_registro,
        datos: dict,
        precios: list[dict],
    ):

        registro = cls.actualizar(
            id_registro,
            datos,
        )

        if registro is None:

            return None

        cls.guardar_precios(
            id_registro,
            precios,
        )

        return cls.obtener_completo(
            id_registro,
        )

    @classmethod
    def obtener_variante_por_id(
        cls,
        id_registro,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(ProductoVariante)
                .filter(
                    ProductoVariante.id == id_registro,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def listar_variantes(
        cls,
        producto_id,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(ProductoVariante)
                .filter(
                    ProductoVariante.producto_id
                    == producto_id,
                )
                .order_by(
                    ProductoVariante.orden,
                    ProductoVariante.codigo,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def buscar_variantes(
        cls,
        texto: str = "",
    ):

        db = SessionLocal()

        try:

            consulta = (
                db.query(
                    ProductoVariante,
                    Producto,
                )
                .join(
                    Producto,
                    ProductoVariante.producto_id
                    == Producto.id,
                )
                .filter(
                    ProductoVariante.activo.is_(True),
                    Producto.activo.is_(True),
                    Producto.maneja_variantes.is_(True),
                )
            )

            texto = texto.strip()

            if texto:

                patron = f"%{texto}%"

                consulta = consulta.filter(
                    or_(
                        ProductoVariante.codigo.ilike(
                            patron,
                        ),
                        ProductoVariante.codigo_barras.ilike(
                            patron,
                        ),
                        ProductoVariante.talla.ilike(
                            patron,
                        ),
                        ProductoVariante.color.ilike(
                            patron,
                        ),
                        ProductoVariante.calibre.ilike(
                            patron,
                        ),
                        ProductoVariante.largo.ilike(
                            patron,
                        ),
                        Producto.nombre.ilike(
                            patron,
                        ),
                        Producto.codigo.ilike(
                            patron,
                        ),
                        cast(
                            ProductoVariante.atributos,
                            String,
                        ).ilike(
                            patron,
                        ),
                    )
                )

            return (
                consulta.order_by(
                    Producto.nombre,
                    ProductoVariante.orden,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def sincronizar_existencia_producto(
        cls,
        producto_id: int,
    ) -> None:

        db = SessionLocal()

        try:

            total = (
                db.query(ProductoVariante)
                .filter(
                    ProductoVariante.producto_id
                    == producto_id,
                    ProductoVariante.activo.is_(True),
                )
                .with_entities(
                    ProductoVariante.existencia,
                )
                .all()
            )

            suma = sum(
                float(
                    valor[0] or 0,
                )
                for valor in total
            )

            producto = (
                db.query(Producto)
                .filter(
                    Producto.id == producto_id,
                )
                .first()
            )

            if producto is not None:

                producto.existencia = suma

                db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def existe_codigo_variante(
        cls,
        codigo,
        excluir_id=None,
    ):

        db = SessionLocal()

        try:

            consulta = (
                db.query(ProductoVariante)
                .filter(
                    ProductoVariante.codigo == codigo,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    ProductoVariante.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def existe_codigo_barras_variante(
        cls,
        codigo_barras,
        excluir_id=None,
    ):

        if not codigo_barras:

            return False

        db = SessionLocal()

        try:

            consulta = (
                db.query(ProductoVariante)
                .filter(
                    ProductoVariante.codigo_barras
                    == codigo_barras,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    ProductoVariante.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def guardar_variantes(
        cls,
        producto_id,
        variantes: list[dict],
    ):

        db = SessionLocal()

        try:

            (
                db.query(ProductoVariante)
                .filter(
                    ProductoVariante.producto_id
                    == producto_id,
                )
                .delete()
            )

            for indice, item in enumerate(variantes):

                registro = ProductoVariante(
                    producto_id=producto_id,
                    codigo=item["codigo"],
                    codigo_barras=item.get(
                        "codigo_barras",
                    ),
                    talla=item.get(
                        "talla",
                    ),
                    color=item.get(
                        "color",
                    ),
                    calibre=item.get(
                        "calibre",
                    ),
                    largo=item.get(
                        "largo",
                    ),
                    atributos=item.get(
                        "atributos",
                    )
                    or {},
                    precio_venta=item.get(
                        "precio_venta",
                    ),
                    costo=item.get(
                        "costo",
                    ),
                    existencia=float(
                        item.get(
                            "existencia",
                            0,
                        )
                        or 0,
                    ),
                    precio_incluye_iva=item.get(
                        "precio_incluye_iva",
                    ),
                    impuesto_venta_id=item.get(
                        "impuesto_venta_id",
                    ),
                    impuesto_compra_id=item.get(
                        "impuesto_compra_id",
                    ),
                    imagen=item.get(
                        "imagen",
                    ),
                    activo=bool(
                        item.get(
                            "activo",
                            True,
                        )
                    ),
                    orden=indice,
                )

                db.add(registro)

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
