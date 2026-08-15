from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import NotaDebitoVenta, NotaDebitoVentaDetalle


class RepositorioNotaDebitoVenta(RepositorioBase):

    modelo = NotaDebitoVenta

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            consulta = db.query(NotaDebitoVenta)

            if texto:

                consulta = consulta.filter(
                    NotaDebitoVenta.numero.ilike(
                        f"%{texto}%",
                    )
                    | NotaDebitoVenta.cufe.ilike(
                        f"%{texto}%",
                    )
                )

            return (
                consulta.order_by(
                    NotaDebitoVenta.fecha.desc(),
                    NotaDebitoVenta.numero.desc(),
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
                db.query(NotaDebitoVenta)
                .filter(
                    NotaDebitoVenta.numero == numero,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    NotaDebitoVenta.id != excluir_id,
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
                db.query(NotaDebitoVenta.numero)
                .filter(
                    NotaDebitoVenta.numero.like(
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
                db.query(NotaDebitoVenta)
                .options(
                    joinedload(
                        NotaDebitoVenta.detalles,
                    ),
                )
                .filter(
                    NotaDebitoVenta.id == id_registro,
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
    def listar_facturas_emitidas(
        cls,
        limite: int = 50,
    ):

        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        db = SessionLocal()

        try:

            return (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.activo.is_(True),
                    FacturaVenta.estado.in_(
                        (
                            "emitida",
                            "generada",
                        ),
                    ),
                )
                .order_by(
                    FacturaVenta.fecha.desc(),
                    FacturaVenta.numero.desc(),
                )
                .limit(limite)
                .all()
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

            registro = NotaDebitoVenta(
                **cabecera,
            )

            db.add(registro)
            db.flush()

            for indice, linea in enumerate(lineas):

                detalle = NotaDebitoVentaDetalle(
                    nota_debito_id=registro.id,
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
                db.query(NotaDebitoVenta)
                .filter(
                    NotaDebitoVenta.id == id_registro,
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

            registro.detalles.clear()

            for indice, linea in enumerate(lineas):

                detalle = NotaDebitoVentaDetalle(
                    nota_debito_id=registro.id,
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
    def actualizar_emision(
        cls,
        id_registro,
        *,
        cufe: str,
        estado: str,
        estado_dian: str,
        mensaje_dian: str,
        ruta_xml: str,
        ruta_zip: str = "",
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(NotaDebitoVenta)
                .filter(
                    NotaDebitoVenta.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.cufe = cufe
            registro.estado = estado
            registro.estado_dian = estado_dian
            registro.mensaje_dian = mensaje_dian
            registro.ruta_xml = ruta_xml

            if ruta_zip:

                registro.ruta_zip = ruta_zip

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
                db.query(NotaDebitoVenta)
                .filter(
                    NotaDebitoVenta.id == id_registro,
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
    def actualizar_contabilizacion(
        cls,
        id_registro,
        *,
        asiento_id: int,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(NotaDebitoVenta)
                .filter(
                    NotaDebitoVenta.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.contabilizado = True
            registro.asiento_id = asiento_id
            registro.estado = "contabilizada"

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def aumentar_saldo_factura(
        cls,
        factura_id: int,
        monto: float,
    ) -> None:

        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        db = SessionLocal()

        try:

            factura = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.id == factura_id,
                )
                .first()
            )

            if factura is None:

                return

            factura.saldo_pendiente = float(
                factura.saldo_pendiente or 0,
            ) + float(
                monto or 0,
            )

            if factura.estado_pago == "pagada":

                factura.estado_pago = "pendiente"

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
