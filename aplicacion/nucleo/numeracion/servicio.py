from __future__ import annotations

from datetime import date

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.nucleo.numeracion.modelos import NumeracionDocumento


class ServicioNumeracion:
    """
    Consecutivos centralizados y atómicos por (codigo_tipo, prefijo).

    Reemplaza el patrón "MAX(numero) + 1 sobre la tabla del
    documento" que usaban los repositorios de cada módulo: ese
    patrón no bloquea la fila, así que dos guardados concurrentes
    pueden calcular el mismo siguiente número. Aquí el consecutivo
    vive en una sola fila por (codigo_tipo, prefijo), tomada con
    ``SELECT ... FOR UPDATE`` antes de incrementarla.

    También valida contra el rango y la vigencia autorizados
    (relevante para prefijos amparados por una resolución DIAN),
    algo que el escaneo de máximos nunca pudo hacer.
    """

    @classmethod
    def siguiente_numero(
        cls,
        codigo_tipo: str,
        prefijo: str,
        *,
        longitud: int = 6,
        resolucion: str | None = None,
        rango_desde: int = 1,
        rango_hasta: int = 999999,
        fecha_inicio: date | None = None,
        fecha_fin: date | None = None,
    ) -> str:

        db = SessionLocal()

        try:

            numeracion = (
                db.query(
                    NumeracionDocumento,
                )
                .filter(
                    NumeracionDocumento.codigo_tipo == codigo_tipo,
                    NumeracionDocumento.prefijo == prefijo,
                )
                .with_for_update()
                .first()
            )

            if numeracion is None:

                numeracion = NumeracionDocumento(
                    codigo_tipo=codigo_tipo,
                    prefijo=prefijo,
                    resolucion=resolucion,
                    rango_desde=rango_desde,
                    rango_hasta=rango_hasta,
                    consecutivo_actual=rango_desde - 1,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    activo=True,
                )

                db.add(
                    numeracion,
                )

                db.flush()

            if not numeracion.activo:

                raise ValueError(
                    f"La numeración '{prefijo}' ({codigo_tipo}) "
                    "está inactiva.",
                )

            if (
                numeracion.fecha_fin is not None
                and date.today() > numeracion.fecha_fin
            ):

                raise ValueError(
                    f"La vigencia de numeración de '{prefijo}' "
                    f"venció el {numeracion.fecha_fin}.",
                )

            siguiente = numeracion.consecutivo_actual + 1

            if siguiente > numeracion.rango_hasta:

                raise ValueError(
                    f"Se agotó el rango autorizado para '{prefijo}' "
                    f"({numeracion.rango_desde}-{numeracion.rango_hasta}).",
                )

            numeracion.consecutivo_actual = siguiente

            db.commit()

            return (
                f"{prefijo}"
                f"{siguiente:0{longitud}d}"
            )

        finally:

            db.close()
