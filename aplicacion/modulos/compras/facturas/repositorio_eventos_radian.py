from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal

from .modelos import (
    FacturaCompra,
    FacturaCompraEventoRadian,
)


class RepositorioFacturaCompraEventoRadian:

    @classmethod
    def registrar(
        cls,
        factura_id: int,
        *,
        codigo: str,
        cude: str = "",
        estado: str = "enviado",
        mensaje: str = "",
        ruta_xml: str = "",
        forzado: bool = False,
    ) -> FacturaCompraEventoRadian:

        db = SessionLocal()

        try:

            evento = FacturaCompraEventoRadian(
                factura_id=factura_id,
                codigo_evento=codigo,
                cude=cude or None,
                estado=estado or "enviado",
                mensaje=mensaje or None,
                ruta_xml=ruta_xml or None,
                forzado=forzado,
                fecha_evento=datetime.now(),
            )

            db.add(evento)

            registro = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.id == factura_id,
                )
                .first()
            )

            if registro is not None:

                registro.evento_radian_codigo = codigo
                registro.evento_radian_cude = cude or None
                registro.evento_radian_mensaje = mensaje or None
                registro.evento_radian_fecha = datetime.now()

            db.commit()
            db.refresh(evento)

            return evento

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def existe_exitoso(
        cls,
        factura_id: int,
        codigo: str,
    ) -> bool:

        db = SessionLocal()

        try:

            return (
                db.query(
                    FacturaCompraEventoRadian.id,
                )
                .filter(
                    FacturaCompraEventoRadian.factura_id
                    == factura_id,
                    FacturaCompraEventoRadian.codigo_evento
                    == codigo,
                    FacturaCompraEventoRadian.estado.in_(
                        (
                            "enviado",
                            "aceptado",
                            "registrado",
                        ),
                    ),
                )
                .first()
                is not None
            )

        finally:

            db.close()

    @classmethod
    def listar_por_factura(
        cls,
        factura_id: int,
    ) -> list[FacturaCompraEventoRadian]:

        db = SessionLocal()

        try:

            return (
                db.query(
                    FacturaCompraEventoRadian,
                )
                .filter(
                    FacturaCompraEventoRadian.factura_id
                    == factura_id,
                )
                .order_by(
                    FacturaCompraEventoRadian.fecha_evento.desc(),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def listar_facturas_pendientes_033(
        cls,
        *,
        dias_plazo: int,
    ) -> list[FacturaCompra]:

        from datetime import date, timedelta

        db = SessionLocal()

        try:

            limite = date.today() - timedelta(
                days=dias_plazo,
            )

            facturas = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.activo.is_(
                        True,
                    ),
                    FacturaCompra.cufe.isnot(
                        None,
                    ),
                    FacturaCompra.fecha <= limite,
                )
                .all()
            )

            pendientes: list[FacturaCompra] = []

            codigos_bloqueo = (
                "032",
                "033",
                "034",
            )

            for factura in facturas:

                if any(
                    cls.existe_exitoso(
                        factura.id,
                        codigo,
                    )
                    for codigo in codigos_bloqueo
                ):

                    continue

                pendientes.append(
                    factura,
                )

            return pendientes

        finally:

            db.close()
