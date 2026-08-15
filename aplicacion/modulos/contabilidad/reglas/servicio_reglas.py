from __future__ import annotations

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.nucleo.configuracion import Configuracion

from aplicacion.modulos.contabilidad.modelos import (
    ReglaContabilizacion,
)


class ServicioReglasContabilizacion:
    """Motor de reglas contables configurables."""

    REGLAS_DEFECTO = (
        {
            "nombre": "Mercancía → Inventario",
            "tipo_operacion": "compra",
            "criterio": "producto_tipo",
            "valor_criterio": "mercancia",
            "cuenta_debito": "143501",
            "cuenta_iva": "240801",
            "cuenta_credito": "220501",
            "prioridad": 10,
        },
        {
            "nombre": "Servicio / papelería → Gasto",
            "tipo_operacion": "compra",
            "criterio": "producto_tipo",
            "valor_criterio": "servicio",
            "cuenta_debito": "613501",
            "cuenta_iva": "240801",
            "cuenta_credito": "220501",
            "prioridad": 20,
        },
        {
            "nombre": "Gasto sin producto",
            "tipo_operacion": "compra",
            "criterio": "sin_producto",
            "valor_criterio": "*",
            "cuenta_debito": "613501",
            "cuenta_iva": "240801",
            "cuenta_credito": "220501",
            "prioridad": 30,
        },
    )

    @classmethod
    def inicializar_defecto(cls) -> None:
        db = SessionLocal()

        try:
            existentes = (
                db.query(ReglaContabilizacion)
                .count()
            )

            if existentes > 0:
                return

            for regla in cls.REGLAS_DEFECTO:
                db.add(
                    ReglaContabilizacion(
                        **regla,
                    )
                )

            db.commit()

        except Exception:
            db.rollback()

        finally:
            db.close()

    @classmethod
    def resolver_cuentas_compra(
        cls,
        *,
        producto_tipo: str | None,
        tiene_producto: bool,
    ) -> dict[str, str]:
        cls.inicializar_defecto()

        db = SessionLocal()

        try:
            consulta = (
                db.query(ReglaContabilizacion)
                .filter(
                    ReglaContabilizacion.tipo_operacion
                    == "compra",
                    ReglaContabilizacion.activo.is_(True),
                )
                .order_by(
                    ReglaContabilizacion.prioridad,
                )
            )

            for regla in consulta.all():
                if cls._coincide(
                    regla,
                    producto_tipo=producto_tipo,
                    tiene_producto=tiene_producto,
                ):
                    return {
                        "debito": regla.cuenta_debito,
                        "iva": regla.cuenta_iva
                        or cls._cuenta_config(
                            "iva_descontable",
                            "240801",
                        ),
                        "credito": regla.cuenta_credito
                        or cls._cuenta_config(
                            "cuentas_por_pagar",
                            "220501",
                        ),
                    }

        except Exception:
            for regla in cls.REGLAS_DEFECTO:
                objeto = ReglaContabilizacion(
                    **regla,
                )

                if cls._coincide(
                    objeto,
                    producto_tipo=producto_tipo,
                    tiene_producto=tiene_producto,
                ):
                    return {
                        "debito": regla["cuenta_debito"],
                        "iva": regla.get(
                            "cuenta_iva",
                            "240801",
                        ),
                        "credito": regla.get(
                            "cuenta_credito",
                            "220501",
                        ),
                    }

        finally:
            db.close()

        if (
            not tiene_producto
            or producto_tipo == "servicio"
        ):
            return {
                "debito": cls._cuenta_config(
                    "gasto_compras",
                    "613501",
                ),
                "iva": cls._cuenta_config(
                    "iva_descontable",
                    "240801",
                ),
                "credito": cls._cuenta_config(
                    "cuentas_por_pagar",
                    "220501",
                ),
            }

        return {
            "debito": cls._cuenta_config(
                "inventario",
                "143501",
            ),
            "iva": cls._cuenta_config(
                "iva_descontable",
                "240801",
            ),
            "credito": cls._cuenta_config(
                "cuentas_por_pagar",
                "220501",
            ),
        }

    @classmethod
    def _coincide(
        cls,
        regla: ReglaContabilizacion,
        *,
        producto_tipo: str | None,
        tiene_producto: bool,
    ) -> bool:
        criterio = regla.criterio
        valor = str(
            regla.valor_criterio or "",
        ).lower()

        if criterio == "sin_producto":
            return not tiene_producto

        if criterio == "producto_tipo":
            if not tiene_producto:
                return valor in (
                    "servicio",
                    "gasto",
                )

            tipo = str(
                producto_tipo or "mercancia",
            ).lower()

            if valor == "mercancia":
                return tipo not in (
                    "servicio",
                )

            return tipo == valor

        return False

    @classmethod
    def _cuenta_config(
        cls,
        clave: str,
        defecto: str,
    ) -> str:
        return str(
            Configuracion.obtener(
                "contabilidad",
                "cuentas",
                clave,
            )
            or defecto
        )

    @classmethod
    def listar(cls) -> list[ReglaContabilizacion]:
        db = SessionLocal()

        try:
            return (
                db.query(ReglaContabilizacion)
                .order_by(
                    ReglaContabilizacion.prioridad,
                )
                .all()
            )

        finally:
            db.close()
