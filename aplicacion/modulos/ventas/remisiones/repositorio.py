from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import RemisionVenta, RemisionVentaDetalle


class RepositorioRemision(RepositorioBase):

    modelo = RemisionVenta

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            consulta = db.query(RemisionVenta)

            if texto:

                consulta = consulta.filter(
                    RemisionVenta.numero.ilike(
                        f"%{texto}%",
                    )
                )

            return (
                consulta.order_by(
                    RemisionVenta.fecha.desc(),
                    RemisionVenta.numero.desc(),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def siguiente_secuencia(
        cls,
        prefijo: str,
    ) -> int:

        db = SessionLocal()

        try:

            numeros = (
                db.query(RemisionVenta.numero)
                .filter(
                    RemisionVenta.numero.like(
                        f"{prefijo}%",
                    )
                )
                .all()
            )

            maximo = 0

            for (numero,) in numeros:

                sufijo = numero[len(prefijo):]

                if sufijo.isdigit():

                    maximo = max(
                        maximo,
                        int(sufijo),
                    )

            return maximo + 1

        finally:

            db.close()

    @classmethod
    def obtener_por_cotizacion(
        cls,
        cotizacion_id: int,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(RemisionVenta)
                .filter(
                    RemisionVenta.cotizacion_id
                    == cotizacion_id,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def obtener_por_pedido(
        cls,
        pedido_id: int,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(RemisionVenta)
                .filter(
                    RemisionVenta.pedido_id
                    == pedido_id,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def obtener_completa(
        cls,
        id_registro,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(RemisionVenta)
                .options(
                    joinedload(
                        RemisionVenta.detalles,
                    ),
                )
                .filter(
                    RemisionVenta.id == id_registro,
                )
                .first()
            )

            if registro is not None:

                list(
                    registro.detalles,
                )

            return registro

        finally:

            db.close()

    @classmethod
    def existe_numero(
        cls,
        numero: str,
        id_registro=None,
    ) -> bool:

        db = SessionLocal()

        try:

            consulta = db.query(
                RemisionVenta,
            ).filter(
                RemisionVenta.numero == numero,
            )

            if id_registro is not None:

                consulta = consulta.filter(
                    RemisionVenta.id != id_registro,
                )

            return (
                consulta.first()
                is not None
            )

        finally:

            db.close()

    @classmethod
    def guardar_completa(
        cls,
        cabecera: dict,
        lineas: list[dict],
    ):

        db = SessionLocal()

        try:

            registro = RemisionVenta(
                **cabecera,
            )

            db.add(registro)
            db.flush()

            for indice, linea in enumerate(lineas):

                detalle = RemisionVentaDetalle(
                    remision_id=registro.id,
                    producto_id=linea.get(
                        "producto_id",
                    ),
                    producto_variante_id=linea.get(
                        "producto_variante_id",
                    ),
                    descripcion=linea[
                        "descripcion"
                    ],
                    cantidad=linea[
                        "cantidad"
                    ],
                    precio_unitario=linea[
                        "precio_unitario"
                    ],
                    impuesto_id=linea.get(
                        "impuesto_id",
                    ),
                    precio_incluye_iva=bool(
                        linea.get(
                            "precio_incluye_iva",
                            False,
                        )
                    ),
                    total_linea=linea[
                        "total_linea"
                    ],
                    orden=indice,
                )

                db.add(detalle)

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_completa(
        cls,
        id_registro,
        cabecera: dict,
        lineas: list[dict],
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(RemisionVenta)
                .filter(
                    RemisionVenta.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            for campo, valor in cabecera.items():

                if hasattr(
                    registro,
                    campo,
                ):

                    setattr(
                        registro,
                        campo,
                        valor,
                    )

            (
                db.query(RemisionVentaDetalle)
                .filter(
                    RemisionVentaDetalle.remision_id
                    == id_registro,
                )
                .delete()
            )

            for indice, linea in enumerate(lineas):

                detalle = RemisionVentaDetalle(
                    remision_id=registro.id,
                    producto_id=linea.get(
                        "producto_id",
                    ),
                    producto_variante_id=linea.get(
                        "producto_variante_id",
                    ),
                    descripcion=linea[
                        "descripcion"
                    ],
                    cantidad=linea[
                        "cantidad"
                    ],
                    precio_unitario=linea[
                        "precio_unitario"
                    ],
                    impuesto_id=linea.get(
                        "impuesto_id",
                    ),
                    precio_incluye_iva=bool(
                        linea.get(
                            "precio_incluye_iva",
                            False,
                        )
                    ),
                    total_linea=linea[
                        "total_linea"
                    ],
                    orden=indice,
                )

                db.add(detalle)

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_despacho(
        cls,
        id_registro,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(RemisionVenta)
                .filter(
                    RemisionVenta.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.estado = "despachada"
            registro.inventario_aplicado = True

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_entrega(
        cls,
        id_registro: int,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(RemisionVenta)
                .filter(
                    RemisionVenta.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.estado = "entregada"

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_estado_confirmacion(
        cls,
        id_registro: int,
        *,
        estado: str,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(RemisionVenta)
                .filter(
                    RemisionVenta.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.estado = estado

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
