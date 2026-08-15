from __future__ import annotations

from datetime import date

from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.modulos.contabilidad.modelos import (
    AsientoContable,
    AsientoDetalle,
    PlanCuenta,
)
from aplicacion.modulos.contabilidad.servicios import (
    ServicioContabilidad,
)


class ServicioComprobantes:

    ORIGEN_MANUAL = "manual"

    @classmethod
    def listar(cls):

        db = SessionLocal()

        try:

            return (
                db.query(AsientoContable)
                .order_by(
                    AsientoContable.fecha.desc(),
                    AsientoContable.id.desc(),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            if not texto:

                return cls.listar()

            return (
                db.query(AsientoContable)
                .filter(
                    AsientoContable.numero.ilike(
                        f"%{texto}%",
                    )
                    | AsientoContable.descripcion.ilike(
                        f"%{texto}%",
                    )
                )
                .order_by(
                    AsientoContable.fecha.desc(),
                )
                .all()
            )

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
                db.query(AsientoContable)
                .options(
                    joinedload(
                        AsientoContable.detalles,
                    ).joinedload(
                        AsientoDetalle.cuenta,
                    ),
                )
                .filter(
                    AsientoContable.id == id_registro,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def _validar_lineas(
        cls,
        lineas: list[dict],
    ):

        if not lineas:

            raise ValueError(
                "Agregue al menos una línea al comprobante.",
            )

        total_debito = 0.0
        total_credito = 0.0

        for indice, linea in enumerate(
            lineas,
            start=1,
        ):

            cuenta_id = linea.get(
                "cuenta_id",
            )

            if not cuenta_id:

                raise ValueError(
                    f"Línea {indice}: seleccione una cuenta.",
                )

            debito = float(
                linea.get(
                    "debito",
                    0,
                )
                or 0,
            )

            credito = float(
                linea.get(
                    "credito",
                    0,
                )
                or 0,
            )

            if debito < 0 or credito < 0:

                raise ValueError(
                    f"Línea {indice}: valores negativos no permitidos.",
                )

            if debito > 0 and credito > 0:

                raise ValueError(
                    f"Línea {indice}: use débito o crédito, no ambos.",
                )

            if debito == 0 and credito == 0:

                raise ValueError(
                    f"Línea {indice}: ingrese débito o crédito.",
                )

            total_debito += debito
            total_credito += credito

        if abs(
            total_debito - total_credito,
        ) > 0.009:

            raise ValueError(
                "El comprobante no cuadra: "
                f"débitos {total_debito:,.2f} "
                f"≠ créditos {total_credito:,.2f}.",
            )

        return total_debito, total_credito

    @classmethod
    def guardar_manual(
        cls,
        cabecera: dict,
        lineas: list[dict],
        id_registro=None,
    ):

        ServicioContabilidad.inicializar_plan()

        fecha = cabecera.get(
            "fecha",
        ) or date.today()

        descripcion = str(
            cabecera.get(
                "descripcion",
                "",
            )
            or "",
        ).strip()

        if not descripcion:

            raise ValueError(
                "La descripción es obligatoria.",
            )

        total_debito, total_credito = (
            cls._validar_lineas(
                lineas,
            )
        )

        db = SessionLocal()

        try:

            if id_registro is None:

                asiento = AsientoContable(
                    numero=ServicioContabilidad._siguiente_numero(
                        db,
                    ),
                    fecha=fecha,
                    descripcion=descripcion,
                    origen=cls.ORIGEN_MANUAL,
                )

                db.add(asiento)
                db.flush()

            else:

                asiento = (
                    db.query(AsientoContable)
                    .filter(
                        AsientoContable.id
                        == id_registro,
                    )
                    .first()
                )

                if asiento is None:

                    raise ValueError(
                        "No se encontró el comprobante.",
                    )

                if (
                    asiento.origen
                    != cls.ORIGEN_MANUAL
                ):

                    raise ValueError(
                        "Solo puede editar comprobantes manuales.",
                    )

                asiento.fecha = fecha
                asiento.descripcion = descripcion

                (
                    db.query(AsientoDetalle)
                    .filter(
                        AsientoDetalle.asiento_id
                        == asiento.id,
                    )
                    .delete(
                        synchronize_session=False,
                    )
                )

            for indice, linea in enumerate(
                lineas,
            ):

                db.add(
                    AsientoDetalle(
                        asiento_id=asiento.id,
                        cuenta_id=int(
                            linea["cuenta_id"],
                        ),
                        debito=float(
                            linea.get(
                                "debito",
                                0,
                            )
                            or 0,
                        ),
                        credito=float(
                            linea.get(
                                "credito",
                                0,
                            )
                            or 0,
                        ),
                        descripcion=str(
                            linea.get(
                                "descripcion",
                                "",
                            )
                            or "",
                        ).strip(),
                        orden=indice,
                    ),
                )

            asiento.total_debito = total_debito
            asiento.total_credito = total_credito

            db.commit()

            return cls.obtener_completo(
                asiento.id,
            )

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def eliminar_manual(
        cls,
        id_registro,
    ):

        db = SessionLocal()

        try:

            asiento = (
                db.query(AsientoContable)
                .filter(
                    AsientoContable.id == id_registro,
                )
                .first()
            )

            if asiento is None:

                return False

            if (
                asiento.origen
                != cls.ORIGEN_MANUAL
            ):

                raise ValueError(
                    "Solo puede eliminar comprobantes manuales.",
                )

            db.delete(asiento)
            db.commit()

            return True

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
