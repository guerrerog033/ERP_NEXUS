from __future__ import annotations

from datetime import (
    date,
    datetime,
    time,
)

from sqlalchemy import func

from aplicacion.comunes.repositorio_base import (
    RepositorioBase,
)
from aplicacion.modulos.ventas.facturas.modelos import (
    FacturaVenta,
)
from aplicacion.modulos.ventas.pos.modelos import (
    PosCierreCaja,
    PosVentaLog,
)


class RepositorioPosVentaLog(
    RepositorioBase,
):

    modelo = PosVentaLog

    @classmethod
    def _rango_dia(
        cls,
        fecha: date,
    ) -> tuple[
        datetime,
        datetime,
    ]:

        return (
            datetime.combine(
                fecha,
                time.min,
            ),
            datetime.combine(
                fecha,
                time.max,
            ),
        )

    @classmethod
    def _aplicar_filtros_historial(
        cls,
        consulta,
        *,
        fecha_desde: date | None,
        fecha_hasta: date | None,
        metodo_pago: str | None,
        usuario: str | None,
    ):

        if fecha_desde is not None:

            inicio, _ = cls._rango_dia(
                fecha_desde,
            )

            consulta = consulta.filter(
                PosVentaLog.fecha_creacion
                >= inicio,
            )

        if fecha_hasta is not None:

            _, fin = cls._rango_dia(
                fecha_hasta,
            )

            consulta = consulta.filter(
                PosVentaLog.fecha_creacion
                <= fin,
            )

        if metodo_pago:

            consulta = consulta.filter(
                PosVentaLog.metodo_pago
                == metodo_pago,
            )

        if usuario:

            consulta = consulta.filter(
                PosVentaLog.usuario.ilike(
                    f"%{usuario.strip()}%",
                ),
            )

        return consulta

    @classmethod
    def listar_historial(
        cls,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        metodo_pago: str | None = None,
        usuario: str | None = None,
        limite: int = 500,
    ) -> list[dict]:

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            consulta = (
                db.query(
                    PosVentaLog,
                    FacturaVenta.numero,
                    FacturaVenta.cliente_id,
                )
                .join(
                    FacturaVenta,
                    PosVentaLog.factura_id
                    == FacturaVenta.id,
                )
            )

            consulta = cls._aplicar_filtros_historial(
                consulta,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                metodo_pago=metodo_pago,
                usuario=usuario,
            )

            filas = (
                consulta.order_by(
                    PosVentaLog.fecha_creacion.desc(),
                )
                .limit(
                    max(
                        1,
                        limite,
                    ),
                )
                .all()
            )

            return [
                {
                    "id": registro.id,
                    "fecha": registro.fecha_creacion,
                    "factura_numero": numero,
                    "cliente_id": cliente_id,
                    "total": registro.total,
                    "recibido": registro.recibido,
                    "cambio": registro.cambio,
                    "metodo_pago": registro.metodo_pago,
                    "usuario": registro.usuario,
                }
                for registro, numero, cliente_id in filas
            ]

        finally:

            db.close()

    @classmethod
    def resumen_caja(
        cls,
        *,
        fecha: date | None = None,
    ) -> dict:

        cls._validar_modelo()

        dia = fecha or date.today()

        inicio, fin = cls._rango_dia(
            dia,
        )

        db = cls.obtener_sesion()

        try:

            totales = (
                db.query(
                    func.count(
                        PosVentaLog.id,
                    ),
                    func.coalesce(
                        func.sum(
                            PosVentaLog.total,
                        ),
                        0,
                    ),
                    func.coalesce(
                        func.sum(
                            PosVentaLog.recibido,
                        ),
                        0,
                    ),
                    func.coalesce(
                        func.sum(
                            PosVentaLog.cambio,
                        ),
                        0,
                    ),
                )
                .filter(
                    PosVentaLog.fecha_creacion
                    >= inicio,
                    PosVentaLog.fecha_creacion
                    <= fin,
                )
                .one()
            )

            por_metodo = (
                db.query(
                    PosVentaLog.metodo_pago,
                    func.count(
                        PosVentaLog.id,
                    ),
                    func.coalesce(
                        func.sum(
                            PosVentaLog.total,
                        ),
                        0,
                    ),
                )
                .filter(
                    PosVentaLog.fecha_creacion
                    >= inicio,
                    PosVentaLog.fecha_creacion
                    <= fin,
                )
                .group_by(
                    PosVentaLog.metodo_pago,
                )
                .all()
            )

            return {
                "fecha": dia,
                "ventas": int(
                    totales[0] or 0,
                ),
                "total": float(
                    totales[1] or 0,
                ),
                "recibido": float(
                    totales[2] or 0,
                ),
                "cambio": float(
                    totales[3] or 0,
                ),
                "por_metodo": [
                    {
                        "metodo_pago": metodo,
                        "ventas": int(
                            cantidad or 0,
                        ),
                        "total": float(
                            monto or 0,
                        ),
                    }
                    for metodo, cantidad, monto in por_metodo
                ],
            }

        finally:

            db.close()

    @classmethod
    def obtener_log_por_id(
        cls,
        log_id: int,
    ) -> dict | None:

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            registro = (
                db.query(
                    PosVentaLog,
                )
                .filter(
                    PosVentaLog.id
                    == log_id,
                )
                .first()
            )

            if registro is None:

                return None

            return {
                "id": registro.id,
                "factura_id": registro.factura_id,
                "total": float(
                    registro.total or 0,
                ),
                "recibido": float(
                    registro.recibido or 0,
                ),
                "cambio": float(
                    registro.cambio or 0,
                ),
                "metodo_pago": registro.metodo_pago,
                "usuario": registro.usuario,
                "fecha": registro.fecha_creacion,
            }

        finally:

            db.close()

    @classmethod
    def obtener_log_por_factura(
        cls,
        factura_id: int,
    ) -> dict | None:

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            registro = (
                db.query(
                    PosVentaLog,
                )
                .filter(
                    PosVentaLog.factura_id
                    == factura_id,
                )
                .order_by(
                    PosVentaLog.fecha_creacion.desc(),
                )
                .first()
            )

            if registro is None:

                return None

            return {
                "id": registro.id,
                "factura_id": registro.factura_id,
                "total": float(
                    registro.total or 0,
                ),
                "recibido": float(
                    registro.recibido or 0,
                ),
                "cambio": float(
                    registro.cambio or 0,
                ),
                "metodo_pago": registro.metodo_pago,
                "usuario": registro.usuario,
                "fecha": registro.fecha_creacion,
            }

        finally:

            db.close()

    @classmethod
    def efectivo_esperado(
        cls,
        *,
        fecha: date | None = None,
    ) -> float:

        cls._validar_modelo()

        dia = fecha or date.today()

        inicio, fin = cls._rango_dia(
            dia,
        )

        db = cls.obtener_sesion()

        try:

            neto = (
                db.query(
                    func.coalesce(
                        func.sum(
                            PosVentaLog.recibido
                            - PosVentaLog.cambio,
                        ),
                        0,
                    ),
                )
                .filter(
                    PosVentaLog.fecha_creacion
                    >= inicio,
                    PosVentaLog.fecha_creacion
                    <= fin,
                    PosVentaLog.metodo_pago
                    == "efectivo",
                )
                .scalar()
            )

            return float(
                neto or 0,
            )

        finally:

            db.close()


class RepositorioPosCierreCaja(
    RepositorioBase,
):

    modelo = PosCierreCaja

    @classmethod
    def obtener_por_fecha(
        cls,
        fecha: date,
    ) -> dict | None:

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            registro = (
                db.query(
                    PosCierreCaja,
                )
                .filter(
                    PosCierreCaja.fecha
                    == fecha,
                )
                .order_by(
                    PosCierreCaja.fecha_cierre.desc(),
                )
                .first()
            )

            if registro is None:

                return None

            return cls._a_dict(
                registro,
            )

        finally:

            db.close()

    @classmethod
    def _a_dict(
        cls,
        registro: PosCierreCaja,
    ) -> dict:

        return {
            "id": registro.id,
            "fecha": registro.fecha,
            "usuario": registro.usuario,
            "efectivo_esperado": float(
                registro.efectivo_esperado or 0,
            ),
            "efectivo_contado": float(
                registro.efectivo_contado or 0,
            ),
            "diferencia": float(
                registro.diferencia or 0,
            ),
            "total_ventas": float(
                registro.total_ventas or 0,
            ),
            "ventas_count": int(
                registro.ventas_count or 0,
            ),
            "observaciones": registro.observaciones,
            "fecha_cierre": registro.fecha_cierre,
        }

    @classmethod
    def registrar(
        cls,
        *,
        fecha: date,
        usuario: str,
        efectivo_esperado: float,
        efectivo_contado: float,
        total_ventas: float,
        ventas_count: int,
        observaciones: str | None = None,
    ) -> dict:

        cls._validar_modelo()

        db = cls.obtener_sesion()

        try:

            existente = (
                db.query(
                    PosCierreCaja,
                )
                .filter(
                    PosCierreCaja.fecha
                    == fecha,
                )
                .first()
            )

            if existente is not None:

                raise ValueError(
                    "La caja de este día ya fue cerrada.",
                )

            diferencia = (
                float(
                    efectivo_contado,
                )
                - float(
                    efectivo_esperado,
                )
            )

            registro = PosCierreCaja(
                fecha=fecha,
                usuario=usuario,
                efectivo_esperado=efectivo_esperado,
                efectivo_contado=efectivo_contado,
                diferencia=diferencia,
                total_ventas=total_ventas,
                ventas_count=ventas_count,
                observaciones=(
                    observaciones or None
                ),
            )

            db.add(
                registro,
            )
            db.commit()
            db.refresh(
                registro,
            )

            return cls._a_dict(
                registro,
            )

        finally:

            db.close()
