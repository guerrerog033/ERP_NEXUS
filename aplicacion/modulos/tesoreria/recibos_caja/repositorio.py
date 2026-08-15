from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase
from aplicacion.modulos.ventas.facturas.modelos import FacturaVenta

from .modelos import ReciboCaja, ReciboCajaDetalle


class RepositorioReciboCaja(RepositorioBase):

    modelo = ReciboCaja

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            consulta = db.query(ReciboCaja)

            if texto:

                consulta = consulta.filter(
                    ReciboCaja.numero.ilike(
                        f"%{texto}%",
                    )
                )

            return (
                consulta.order_by(
                    ReciboCaja.fecha.desc(),
                    ReciboCaja.numero.desc(),
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
                db.query(ReciboCaja.numero)
                .filter(
                    ReciboCaja.numero.like(
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
    def obtener_completo(
        cls,
        id_registro,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(ReciboCaja)
                .options(
                    joinedload(
                        ReciboCaja.detalles,
                    ),
                )
                .filter(
                    ReciboCaja.id == id_registro,
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
    def listar_facturas_pendientes(
        cls,
        cliente_id: int,
    ) -> list[FacturaVenta]:

        db = SessionLocal()

        try:

            return (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.cliente_id
                    == cliente_id,
                    FacturaVenta.contabilizado
                    == True,  # noqa: E712
                    FacturaVenta.activo
                    == True,  # noqa: E712
                    FacturaVenta.saldo_pendiente
                    > 0,
                )
                .order_by(
                    FacturaVenta.fecha.asc(),
                    FacturaVenta.numero.asc(),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def guardar_completo(
        cls,
        cabecera: dict,
        lineas: list[dict],
        *,
        id_registro=None,
    ):

        db = SessionLocal()

        try:

            if id_registro is None:

                registro = ReciboCaja(
                    **cabecera,
                )

                db.add(registro)
                db.flush()

            else:

                registro = (
                    db.query(ReciboCaja)
                    .filter(
                        ReciboCaja.id
                        == id_registro,
                    )
                    .first()
                )

                if registro is None:

                    return None

                if registro.contabilizado:

                    raise ValueError(
                        "El recibo ya fue contabilizado.",
                    )

                for campo, valor in cabecera.items():

                    setattr(
                        registro,
                        campo,
                        valor,
                    )

                (
                    db.query(ReciboCajaDetalle)
                    .filter(
                        ReciboCajaDetalle.recibo_id
                        == id_registro,
                    )
                    .delete()
                )

                db.flush()

            for indice, linea in enumerate(lineas):

                db.add(
                    ReciboCajaDetalle(
                        recibo_id=registro.id,
                        factura_venta_id=linea[
                            "factura_venta_id"
                        ],
                        valor_aplicado=linea[
                            "valor_aplicado"
                        ],
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
    def actualizar_contabilizacion(
        cls,
        id_registro,
        *,
        asiento_id: int,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(ReciboCaja)
                .filter(
                    ReciboCaja.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.contabilizado = True
            registro.asiento_id = asiento_id
            registro.estado = "contabilizado"

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def aplicar_pago_facturas(
        cls,
        lineas: list[dict],
    ) -> None:

        db = SessionLocal()

        try:

            for linea in lineas:

                factura = (
                    db.query(FacturaVenta)
                    .filter(
                        FacturaVenta.id
                        == linea[
                            "factura_venta_id"
                        ],
                    )
                    .first()
                )

                if factura is None:

                    continue

                valor = float(
                    linea["valor_aplicado"],
                )

                factura.valor_pagado = float(
                    factura.valor_pagado or 0,
                ) + valor

                factura.saldo_pendiente = max(
                    float(
                        factura.saldo_pendiente or 0,
                    )
                    - valor,
                    0.0,
                )

                from aplicacion.modulos.tesoreria.utilidades import (
                    calcular_estado_pago,
                )

                factura.estado_pago = (
                    calcular_estado_pago(
                        factura.total,
                        factura.valor_pagado,
                    )
                )

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
