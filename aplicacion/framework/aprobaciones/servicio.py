from __future__ import annotations

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.nucleo.configuracion import Configuracion


class ServicioAprobaciones:
    """Flujos de aprobación configurables."""

    REGLAS_DEFECTO = (
        {
            "modulo": "compra",
            "monto_maximo": 5_000_000,
            "aprobador": "jefe_compras",
            "nivel": 1,
        },
        {
            "modulo": "compra",
            "monto_maximo": 20_000_000,
            "aprobador": "gerente_financiero",
            "nivel": 2,
        },
        {
            "modulo": "pago",
            "monto_maximo": 20_000_000,
            "aprobador": "doble_aprobacion",
            "nivel": 3,
        },
    )

    @classmethod
    def requiere_aprobacion(
        cls,
        *,
        modulo: str,
        monto: float,
    ) -> dict | None:
        reglas = Configuracion.obtener(
            "aprobaciones",
            "reglas",
        ) or cls.REGLAS_DEFECTO

        candidatas = [
            r
            for r in reglas
            if r.get("modulo") == modulo
            and float(monto)
            > float(
                r.get(
                    "monto_maximo",
                    0,
                )
            )
        ]

        if not candidatas:
            return None

        return sorted(
            candidatas,
            key=lambda r: r.get(
                "nivel",
                0,
            ),
        )[-1]

    @classmethod
    def solicitar(
        cls,
        *,
        modulo: str,
        documento_id: int,
        monto: float,
        solicitante: str,
    ):
        from aplicacion.framework.aprobaciones.modelos import (
            SolicitudAprobacion,
        )

        regla = cls.requiere_aprobacion(
            modulo=modulo,
            monto=monto,
        )

        if regla is None:
            return None

        db = SessionLocal()

        try:
            solicitud = SolicitudAprobacion(
                modulo=modulo,
                documento_id=documento_id,
                monto=monto,
                aprobador_rol=regla.get(
                    "aprobador",
                    "",
                ),
                solicitante=solicitante,
                estado="pendiente",
            )
            db.add(solicitud)
            db.commit()
            db.refresh(solicitud)

            return solicitud

        finally:
            db.close()

    @classmethod
    def aprobar(
        cls,
        solicitud_id: int,
        *,
        usuario: str,
    ) -> None:
        from aplicacion.framework.aprobaciones.modelos import (
            SolicitudAprobacion,
        )

        db = SessionLocal()

        try:
            solicitud = (
                db.query(SolicitudAprobacion)
                .filter(
                    SolicitudAprobacion.id
                    == solicitud_id,
                )
                .first()
            )

            if solicitud is None:
                raise ValueError(
                    "Solicitud no encontrada.",
                )

            solicitud.estado = "aprobada"
            solicitud.aprobado_por = usuario
            db.commit()

        finally:
            db.close()
