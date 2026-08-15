from __future__ import annotations

from datetime import date

from sqlalchemy import func

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.modulos.contabilidad.modelos import (
    AsientoContable,
    AsientoDetalle,
    PlanCuenta,
)


def _es_costo_venta(
    cuenta: PlanCuenta,
) -> bool:

    codigo = str(
        cuenta.codigo or "",
    ).strip()

    if codigo.startswith(
        "6135",
    ):

        return True

    nombre = str(
        cuenta.nombre or "",
    ).lower()

    return (
        "costo de vent" in nombre
        or "costos de vent" in nombre
    )


class ServicioReportesContables:

    @classmethod
    def balance_prueba(
        cls,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ):

        if fecha_hasta is None:

            fecha_hasta = date.today()

        db = SessionLocal()

        try:

            cuentas = (
                db.query(PlanCuenta)
                .filter(
                    PlanCuenta.activo.is_(True),
                )
                .order_by(
                    PlanCuenta.codigo,
                )
                .all()
            )

            filas = []

            total_debito = 0.0
            total_credito = 0.0

            for cuenta in cuentas:

                consulta = (
                    db.query(
                        func.coalesce(
                            func.sum(
                                AsientoDetalle.debito,
                            ),
                            0,
                        ),
                        func.coalesce(
                            func.sum(
                                AsientoDetalle.credito,
                            ),
                            0,
                        ),
                    )
                    .join(
                        AsientoContable,
                        AsientoContable.id
                        == AsientoDetalle.asiento_id,
                    )
                    .filter(
                        AsientoDetalle.cuenta_id
                        == cuenta.id,
                    )
                )

                if fecha_desde is not None:

                    consulta = consulta.filter(
                        AsientoContable.fecha
                        >= fecha_desde,
                    )

                consulta = consulta.filter(
                    AsientoContable.fecha
                    <= fecha_hasta,
                )

                debito, credito = consulta.one()

                debito = float(
                    debito or 0,
                )

                credito = float(
                    credito or 0,
                )

                if (
                    debito == 0
                    and credito == 0
                ):

                    continue

                saldo = debito - credito

                filas.append(
                    {
                        "codigo": cuenta.codigo,
                        "nombre": cuenta.nombre,
                        "tipo": cuenta.tipo,
                        "debito": debito,
                        "credito": credito,
                        "saldo": saldo,
                    },
                )

                total_debito += debito
                total_credito += credito

            return {
                "filas": filas,
                "total_debito": total_debito,
                "total_credito": total_credito,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
            }

        finally:

            db.close()

    @classmethod
    def libro_mayor(
        cls,
        *,
        cuenta_id: int,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ):

        if fecha_hasta is None:

            fecha_hasta = date.today()

        db = SessionLocal()

        try:

            cuenta = (
                db.query(PlanCuenta)
                .filter(
                    PlanCuenta.id == cuenta_id,
                )
                .first()
            )

            if cuenta is None:

                raise ValueError(
                    "Seleccione una cuenta válida.",
                )

            consulta = (
                db.query(
                    AsientoContable,
                    AsientoDetalle,
                )
                .join(
                    AsientoDetalle,
                    AsientoDetalle.asiento_id
                    == AsientoContable.id,
                )
                .filter(
                    AsientoDetalle.cuenta_id
                    == cuenta_id,
                )
            )

            if fecha_desde is not None:

                consulta = consulta.filter(
                    AsientoContable.fecha
                    >= fecha_desde,
                )

            consulta = consulta.filter(
                AsientoContable.fecha
                <= fecha_hasta,
            )

            registros = consulta.order_by(
                AsientoContable.fecha,
                AsientoContable.numero,
                AsientoDetalle.orden,
            ).all()

            saldo = 0.0
            filas = []

            for asiento, detalle in registros:

                debito = float(
                    detalle.debito or 0,
                )

                credito = float(
                    detalle.credito or 0,
                )

                saldo += debito - credito

                filas.append(
                    {
                        "fecha": asiento.fecha,
                        "numero": asiento.numero,
                        "descripcion": (
                            detalle.descripcion
                            or asiento.descripcion
                            or ""
                        ),
                        "debito": debito,
                        "credito": credito,
                        "saldo": saldo,
                    },
                )

            return {
                "cuenta": cuenta,
                "filas": filas,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
            }

        finally:

            db.close()

    @classmethod
    def libro_mayor_por_codigo(
        cls,
        *,
        codigo_cuenta: str,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ):

        codigo = codigo_cuenta.strip()

        if not codigo:

            raise ValueError(
                "Indique el código de la cuenta.",
            )

        db = SessionLocal()

        try:

            cuenta = (
                db.query(PlanCuenta)
                .filter(
                    PlanCuenta.codigo == codigo,
                )
                .first()
            )

            if cuenta is None:

                raise ValueError(
                    f"No existe la cuenta {codigo}.",
                )

            cuenta_id = cuenta.id

        finally:

            db.close()

        return cls.libro_mayor(
            cuenta_id=cuenta_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

    @classmethod
    def estado_resultados(
        cls,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ):

        if fecha_hasta is None:

            fecha_hasta = date.today()

        db = SessionLocal()

        try:

            cuentas = (
                db.query(PlanCuenta)
                .filter(
                    PlanCuenta.activo.is_(True),
                    PlanCuenta.tipo.in_(
                        [
                            "ingreso",
                            "gasto",
                        ],
                    ),
                )
                .order_by(
                    PlanCuenta.codigo,
                )
                .all()
            )

            ingresos: list[dict] = []
            costos_venta: list[dict] = []
            gastos: list[dict] = []
            total_ingresos = 0.0
            total_costos_venta = 0.0
            total_gastos = 0.0

            for cuenta in cuentas:

                consulta = (
                    db.query(
                        func.coalesce(
                            func.sum(
                                AsientoDetalle.debito,
                            ),
                            0,
                        ),
                        func.coalesce(
                            func.sum(
                                AsientoDetalle.credito,
                            ),
                            0,
                        ),
                    )
                    .join(
                        AsientoContable,
                        AsientoContable.id
                        == AsientoDetalle.asiento_id,
                    )
                    .filter(
                        AsientoDetalle.cuenta_id
                        == cuenta.id,
                    )
                )

                if fecha_desde is not None:

                    consulta = consulta.filter(
                        AsientoContable.fecha
                        >= fecha_desde,
                    )

                consulta = consulta.filter(
                    AsientoContable.fecha
                    <= fecha_hasta,
                )

                debito, credito = consulta.one()

                debito = float(
                    debito or 0,
                )

                credito = float(
                    credito or 0,
                )

                if cuenta.tipo == "ingreso":

                    valor = credito - debito

                else:

                    valor = debito - credito

                if valor == 0:

                    continue

                fila = {
                    "codigo": cuenta.codigo,
                    "nombre": cuenta.nombre,
                    "tipo": cuenta.tipo,
                    "valor": valor,
                }

                if cuenta.tipo == "ingreso":

                    ingresos.append(
                        fila,
                    )
                    total_ingresos += valor

                elif _es_costo_venta(
                    cuenta,
                ):

                    costos_venta.append(
                        fila,
                    )
                    total_costos_venta += valor

                else:

                    gastos.append(
                        fila,
                    )
                    total_gastos += valor

            utilidad_bruta = (
                total_ingresos
                - total_costos_venta
            )

            return {
                "ingresos": ingresos,
                "costos_venta": costos_venta,
                "gastos": gastos,
                "total_ingresos": total_ingresos,
                "total_costos_venta": total_costos_venta,
                "total_gastos": total_gastos,
                "utilidad_bruta": utilidad_bruta,
                "utilidad_neta": utilidad_bruta
                - total_gastos,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
            }

        finally:

            db.close()
