from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import FacturaVenta, FacturaVentaDetalle


class RepositorioFacturaVenta(RepositorioBase):

    modelo = FacturaVenta

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            consulta = db.query(FacturaVenta)

            if texto:

                consulta = consulta.filter(
                    FacturaVenta.numero.ilike(
                        f"%{texto}%",
                    )
                    | FacturaVenta.cufe.ilike(
                        f"%{texto}%",
                    )
                )

            return (
                consulta.order_by(
                    FacturaVenta.fecha.desc(),
                    FacturaVenta.numero.desc(),
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
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.numero == numero,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    FacturaVenta.id != excluir_id,
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
                db.query(FacturaVenta.numero)
                .filter(
                    FacturaVenta.numero.like(
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
                db.query(FacturaVenta)
                .options(
                    joinedload(
                        FacturaVenta.detalles,
                    ),
                )
                .filter(
                    FacturaVenta.id == id_registro,
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
    def obtener_por_cotizacion(
        cls,
        cotizacion_id: int,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.cotizacion_id
                    == cotizacion_id,
                )
                .first()
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

            registro = FacturaVenta(
                **cabecera,
            )

            db.add(registro)
            db.flush()

            for indice, linea in enumerate(lineas):

                detalle = FacturaVentaDetalle(
                    factura_id=registro.id,
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
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.id == id_registro,
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

                detalle = FacturaVentaDetalle(
                    factura_id=registro.id,
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
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.id == id_registro,
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
            registro.ruta_zip = ruta_zip

            db.commit()
            db.refresh(
                registro,
            )

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
                db.query(
                    FacturaVenta,
                )
                .filter(
                    FacturaVenta.id
                    == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.estado = estado

            db.commit()
            db.refresh(
                registro,
            )

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_formato_impresion(
        cls,
        id_registro,
        *,
        formato: str,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.formato_impresion = formato

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
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.contabilizado = True
            registro.asiento_id = asiento_id
            registro.estado = "contabilizada"

            if float(
                registro.saldo_pendiente or 0,
            ) <= 0 and float(
                registro.total or 0,
            ) > 0:

                registro.saldo_pendiente = float(
                    registro.total or 0,
                )
                registro.valor_pagado = 0
                registro.estado_pago = "pendiente"

            from aplicacion.modulos.cartera.servicios import (
                ServicioCartera,
            )

            ServicioCartera.asegurar_fecha_vencimiento_factura_venta(
                registro,
                db,
            )

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
