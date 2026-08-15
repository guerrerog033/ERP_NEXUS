from __future__ import annotations

from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import (
    OrdenCompra,
    OrdenCompraDetalle,
    RecepcionCompra,
)


class RepositorioOrdenCompra(RepositorioBase):

    modelo = OrdenCompra

    @classmethod
    def siguiente_secuencia(
        cls,
        prefijo: str,
    ) -> int:

        db = SessionLocal()

        try:

            numeros = (
                db.query(OrdenCompra.numero)
                .filter(
                    OrdenCompra.numero.like(
                        f"{prefijo}%",
                    ),
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
        id_registro: int,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(OrdenCompra)
                .options(
                    joinedload(
                        OrdenCompra.detalles,
                    ),
                )
                .filter(
                    OrdenCompra.id == id_registro,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def listar_pendientes_recepcion(
        cls,
    ) -> list[OrdenCompra]:

        db = SessionLocal()

        try:

            ordenes = (
                db.query(OrdenCompra)
                .options(
                    joinedload(
                        OrdenCompra.detalles,
                    ),
                )
                .filter(
                    OrdenCompra.activo.is_(
                        True,
                    ),
                    OrdenCompra.estado.in_(
                        [
                            "pendiente",
                            "parcial",
                        ],
                    ),
                )
                .order_by(
                    OrdenCompra.fecha.desc(),
                    OrdenCompra.numero.desc(),
                )
                .all()
            )

            pendientes = []

            for orden in ordenes:

                for detalle in orden.detalles:

                    pendiente = float(
                        detalle.cantidad or 0,
                    ) - float(
                        detalle.cantidad_recibida
                        or 0,
                    )

                    if pendiente > 0:

                        pendientes.append(
                            orden,
                        )

                        break

            return pendientes

        finally:

            db.close()


class RepositorioRecepcionCompra(RepositorioBase):

    modelo = RecepcionCompra

    @classmethod
    def siguiente_secuencia(
        cls,
        prefijo: str,
    ) -> int:

        db = SessionLocal()

        try:

            numeros = (
                db.query(RecepcionCompra.numero)
                .filter(
                    RecepcionCompra.numero.like(
                        f"{prefijo}%",
                    ),
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
