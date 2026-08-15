from __future__ import annotations

from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import (
    NotaCreditoCompra,
    NotaCreditoCompraDetalle,
)


class RepositorioNotaCreditoCompra(RepositorioBase):

    modelo = NotaCreditoCompra

    @classmethod
    def obtener_completa(
        cls,
        id_registro: int,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(NotaCreditoCompra)
                .options(
                    joinedload(
                        NotaCreditoCompra.detalles,
                    ),
                )
                .filter(
                    NotaCreditoCompra.id
                    == id_registro,
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

            registro = NotaCreditoCompra(
                **{
                    k: v
                    for k, v in cabecera.items()
                    if k != "id"
                },
            )

            db.add(registro)
            db.flush()

            for indice, linea in enumerate(
                lineas,
            ):

                db.add(
                    NotaCreditoCompraDetalle(
                        nota_credito_id=registro.id,
                        producto_id=linea.get(
                            "producto_id",
                        ),
                        producto_variante_id=linea.get(
                            "producto_variante_id",
                        ),
                        descripcion=linea[
                            "descripcion"
                        ],
                        cantidad=linea.get(
                            "cantidad",
                            1,
                        ),
                        precio_unitario=linea.get(
                            "precio_unitario",
                            0,
                        ),
                        impuesto_id=linea.get(
                            "impuesto_id",
                        ),
                        precio_incluye_iva=linea.get(
                            "precio_incluye_iva",
                            False,
                        ),
                        total_linea=linea.get(
                            "total_linea",
                            0,
                        ),
                        orden=indice,
                    ),
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
    def actualizar_aplicacion(
        cls,
        id_registro: int,
        *,
        asiento_id: int | None = None,
        inventario_aplicado: bool = False,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(NotaCreditoCompra)
                .filter(
                    NotaCreditoCompra.id
                    == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.estado = "aplicada"
            registro.contabilizado = True
            registro.inventario_aplicado = (
                inventario_aplicado
            )

            if asiento_id:

                registro.asiento_id = asiento_id

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def reducir_saldo_factura_compra(
        cls,
        factura_id: int,
        monto: float,
    ) -> None:

        from aplicacion.modulos.compras.facturas.modelos import (
            FacturaCompra,
        )

        db = SessionLocal()

        try:

            factura = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.id == factura_id,
                )
                .first()
            )

            if factura is None:

                return

            saldo = max(
                float(
                    factura.saldo_pendiente or 0,
                )
                - float(monto or 0),
                0.0,
            )

            factura.saldo_pendiente = saldo

            pagado = float(
                factura.valor_pagado or 0,
            ) + float(monto or 0)

            factura.valor_pagado = pagado

            if saldo <= 0:

                factura.estado_pago = "pagada"

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def listar_facturas_contabilizadas(
        cls,
        limite: int = 50,
    ):

        from aplicacion.modulos.compras.facturas.modelos import (
            FacturaCompra,
        )

        db = SessionLocal()

        try:

            return (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.activo.is_(
                        True,
                    ),
                    FacturaCompra.contabilizado.is_(
                        True,
                    ),
                )
                .order_by(
                    FacturaCompra.fecha.desc(),
                    FacturaCompra.numero.desc(),
                )
                .limit(limite)
                .all()
            )

        finally:

            db.close()
