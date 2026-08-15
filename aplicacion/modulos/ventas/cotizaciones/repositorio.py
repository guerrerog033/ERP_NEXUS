from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import Cotizacion, CotizacionDetalle


class RepositorioCotizacion(RepositorioBase):

    modelo = Cotizacion

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            return (
                db.query(Cotizacion)
                .filter(
                    Cotizacion.numero.ilike(
                        f"%{texto}%",
                    )
                )
                .order_by(
                    Cotizacion.fecha.desc(),
                    Cotizacion.numero.desc(),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def existe_numero(
        cls,
        numero,
        excluir_id=None,
    ):

        db = SessionLocal()

        try:

            consulta = (
                db.query(Cotizacion)
                .filter(
                    Cotizacion.numero == numero,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    Cotizacion.id != excluir_id,
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

            numeros = (
                db.query(Cotizacion.numero)
                .filter(
                    Cotizacion.numero.like(
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
    def obtener_completa(
        cls,
        id_registro,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(Cotizacion)
                .options(
                    joinedload(
                        Cotizacion.detalles,
                    ),
                )
                .filter(
                    Cotizacion.id == id_registro,
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
    def guardar_completa(
        cls,
        cabecera: dict,
        lineas: list[dict],
    ):

        db = SessionLocal()

        try:

            registro = Cotizacion(
                **cabecera,
            )

            db.add(registro)
            db.flush()

            for indice, linea in enumerate(lineas):

                detalle = CotizacionDetalle(
                    cotizacion_id=registro.id,
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
                    retefuente_id=linea.get(
                        "retefuente_id",
                    ),
                    reteica_id=linea.get(
                        "reteica_id",
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
                db.query(Cotizacion)
                .filter(
                    Cotizacion.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            for campo, valor in cabecera.items():

                setattr(
                    registro,
                    campo,
                    valor,
                )

            (
                db.query(CotizacionDetalle)
                .filter(
                    CotizacionDetalle.cotizacion_id
                    == id_registro,
                )
                .delete()
            )

            for indice, linea in enumerate(lineas):

                detalle = CotizacionDetalle(
                    cotizacion_id=registro.id,
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
                    retefuente_id=linea.get(
                        "retefuente_id",
                    ),
                    reteica_id=linea.get(
                        "reteica_id",
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
    def actualizar_campos(
        cls,
        id_registro: int,
        campos: dict,
    ) -> None:
        db = SessionLocal()

        try:
            registro = (
                db.query(Cotizacion)
                .filter(
                    Cotizacion.id == id_registro,
                )
                .first()
            )

            if registro is None:
                return

            for clave, valor in campos.items():
                setattr(
                    registro,
                    clave,
                    valor,
                )

            db.commit()

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
                db.query(Cotizacion)
                .filter(
                    Cotizacion.id == id_registro,
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

    @classmethod
    def obtener_por_codigo_aceptacion(
        cls,
        codigo: str,
    ):
        db = SessionLocal()

        try:
            return (
                db.query(Cotizacion)
                .filter(
                    Cotizacion.codigo_aceptacion
                    == codigo,
                )
                .first()
            )

        finally:
            db.close()
