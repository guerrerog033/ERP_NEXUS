from datetime import datetime

from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import FacturaCompra, FacturaCompraDetalle


class RepositorioFacturaCompra(RepositorioBase):

    modelo = FacturaCompra

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            consulta = db.query(FacturaCompra)

            if texto:

                consulta = consulta.filter(
                    FacturaCompra.numero.ilike(
                        f"%{texto}%",
                    )
                    | FacturaCompra.numero_proveedor.ilike(
                        f"%{texto}%",
                    )
                    | FacturaCompra.cufe.ilike(
                        f"%{texto}%",
                    )
                    | FacturaCompra.nit_proveedor.ilike(
                        f"%{texto}%",
                    )
                )

            return (
                consulta.order_by(
                    FacturaCompra.fecha.desc(),
                    FacturaCompra.numero.desc(),
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
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.numero == numero,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    FacturaCompra.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def existe_cufe(
        cls,
        cufe,
        excluir_id=None,
    ):

        if not cufe:

            return False

        db = SessionLocal()

        try:

            consulta = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.cufe == cufe,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    FacturaCompra.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()

    @classmethod
    def obtener_por_cufe(
        cls,
        cufe: str,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.cufe == cufe,
                )
                .first()
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
                db.query(FacturaCompra.numero)
                .filter(
                    FacturaCompra.numero.like(
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
                db.query(FacturaCompra)
                .options(
                    joinedload(
                        FacturaCompra.detalles,
                    ),
                )
                .filter(
                    FacturaCompra.id == id_registro,
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

            registro = FacturaCompra(
                **cabecera,
            )

            db.add(registro)
            db.flush()

            for indice, linea in enumerate(lineas):

                detalle = FacturaCompraDetalle(
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
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.id == id_registro,
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
                db.query(FacturaCompraDetalle)
                .filter(
                    FacturaCompraDetalle.factura_id
                    == id_registro,
                )
                .delete()
            )

            for indice, linea in enumerate(lineas):

                detalle = FacturaCompraDetalle(
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
    def actualizar_validacion_cufe(
        cls,
        id_registro,
        *,
        valido: bool,
        estado: str = "",
        mensaje: str = "",
    ):

        from datetime import datetime

        db = SessionLocal()

        try:

            registro = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.cufe_validado = bool(
                valido,
            )
            registro.cufe_estado_dian = estado
            registro.cufe_mensaje_dian = mensaje
            registro.cufe_validado_en = datetime.now()

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_acuse_recibo(
        cls,
        id_registro,
        *,
        estado: str,
        cude: str = "",
        mensaje: str = "",
        ruta_xml: str = "",
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.acuse_recibo_estado = estado
            registro.acuse_recibo_cude = cude or None
            registro.acuse_recibo_mensaje = mensaje or None
            registro.ruta_acuse_xml = ruta_xml or None
            registro.acuse_recibo_fecha = datetime.now()

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_evento_radian(
        cls,
        id_registro,
        *,
        codigo: str,
        cude: str = "",
        mensaje: str = "",
    ):

        from aplicacion.modulos.compras.facturas.repositorio_eventos_radian import (
            RepositorioFacturaCompraEventoRadian,
        )

        return RepositorioFacturaCompraEventoRadian.registrar(
            id_registro,
            codigo=codigo,
            cude=cude,
            mensaje=mensaje,
        )

    @classmethod
    def contar_pendientes_revision(cls) -> int:

        db = SessionLocal()

        try:

            return (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.estado
                    == "pendiente_revision",
                    FacturaCompra.activo.is_(True),
                )
                .count()
            )

        finally:

            db.close()

    @classmethod
    def actualizar_estado(
        cls,
        id_registro,
        estado: str,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.id == id_registro,
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
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.id == id_registro,
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

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def vincular_orden_compra(
        cls,
        id_registro: int,
        orden_id: int,
        detalle_map: dict[int, int],
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(FacturaCompra)
                .options(
                    joinedload(
                        FacturaCompra.detalles,
                    ),
                )
                .filter(
                    FacturaCompra.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.orden_compra_id = orden_id

            for detalle in registro.detalles:

                orden_detalle_id = detalle_map.get(
                    detalle.id,
                )

                if orden_detalle_id:

                    detalle.orden_detalle_id = (
                        orden_detalle_id
                    )

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_match(
        cls,
        id_registro: int,
        *,
        estado: str,
        mensaje: str = "",
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.match_estado = estado
            registro.match_mensaje = mensaje

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_inventario_aplicado(
        cls,
        id_registro: int,
        *,
        valor: bool = True,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.inventario_aplicado = valor

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
