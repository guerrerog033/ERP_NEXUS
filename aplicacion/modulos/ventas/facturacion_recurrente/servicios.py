from __future__ import annotations

from datetime import date

from aplicacion.base_datos.conexion import SessionLocal

from .modelos import FacturaRecurrente, FacturaRecurrenteDetalle
from .utilidades import PERIODICIDADES, calcular_proxima_fecha

_CODIGOS_PERIODICIDAD = {
    codigo for codigo, _ in PERIODICIDADES
}


class ServicioFacturaRecurrente:

    @classmethod
    def listar(cls) -> list[dict]:

        from aplicacion.maestros.terceros.modelos import Tercero

        db = SessionLocal()

        try:

            plantillas = (
                db.query(FacturaRecurrente)
                .order_by(
                    FacturaRecurrente.proxima_fecha,
                )
                .all()
            )

            cliente_ids = {
                plantilla.cliente_id
                for plantilla in plantillas
            }

            clientes = {
                tercero.id: tercero
                for tercero in (
                    db.query(Tercero)
                    .filter(Tercero.id.in_(cliente_ids))
                    .all()
                    if cliente_ids
                    else []
                )
            }

            filas = []

            for plantilla in plantillas:

                cliente = clientes.get(
                    plantilla.cliente_id,
                )

                nombre_cliente = (
                    cliente.nombre_completo
                    if cliente is not None
                    else ""
                )

                filas.append(
                    {
                        "id": plantilla.id,
                        "nombre": plantilla.nombre,
                        "cliente": nombre_cliente,
                        "periodicidad": (
                            plantilla.periodicidad
                        ),
                        "proxima_fecha": (
                            plantilla.proxima_fecha
                        ),
                        "facturas_generadas": (
                            plantilla.facturas_generadas
                        ),
                        "activa": plantilla.activa,
                    },
                )

            return filas

        finally:

            db.close()

    @classmethod
    def _validar(
        cls,
        datos: dict,
        lineas: list[dict],
    ) -> None:

        if not str(datos.get("nombre", "")).strip():

            raise ValueError(
                "El nombre de la plantilla es obligatorio.",
            )

        if not datos.get("cliente_id"):

            raise ValueError(
                "Seleccione un cliente.",
            )

        if datos.get("periodicidad") not in (
            _CODIGOS_PERIODICIDAD
        ):

            raise ValueError(
                "Seleccione una periodicidad válida.",
            )

        if not lineas:

            raise ValueError(
                "Agregue al menos una línea.",
            )

    @classmethod
    def guardar(
        cls,
        datos: dict,
        lineas: list[dict],
        *,
        id_registro: int | None = None,
    ) -> FacturaRecurrente:

        cls._validar(datos, lineas)

        db = SessionLocal()

        try:

            if id_registro is not None:

                plantilla = (
                    db.query(FacturaRecurrente)
                    .filter(
                        FacturaRecurrente.id
                        == id_registro,
                    )
                    .first()
                )

                if plantilla is None:

                    raise ValueError(
                        "Plantilla no encontrada.",
                    )

                (
                    db.query(FacturaRecurrenteDetalle)
                    .filter(
                        FacturaRecurrenteDetalle
                        .plantilla_id
                        == id_registro,
                    )
                    .delete()
                )

            else:

                plantilla = FacturaRecurrente()

                db.add(plantilla)

            plantilla.nombre = str(
                datos["nombre"],
            ).strip()
            plantilla.cliente_id = datos["cliente_id"]
            plantilla.periodicidad = datos["periodicidad"]
            plantilla.proxima_fecha = datos[
                "proxima_fecha"
            ]
            plantilla.observaciones = datos.get(
                "observaciones",
                "",
            )
            plantilla.activa = bool(
                datos.get("activa", True),
            )

            db.flush()

            for indice, linea in enumerate(lineas):

                db.add(
                    FacturaRecurrenteDetalle(
                        plantilla_id=plantilla.id,
                        producto_id=linea.get(
                            "producto_id",
                        ),
                        descripcion=str(
                            linea.get(
                                "descripcion",
                                "",
                            )
                            or "Producto/servicio",
                        ).strip(),
                        cantidad=float(
                            linea.get("cantidad", 1)
                            or 1,
                        ),
                        precio_unitario=float(
                            linea.get(
                                "precio_unitario",
                                0,
                            )
                            or 0,
                        ),
                        impuesto_id=linea.get(
                            "impuesto_id",
                        ),
                        precio_incluye_iva=bool(
                            linea.get(
                                "precio_incluye_iva",
                                False,
                            ),
                        ),
                        orden=indice,
                    ),
                )

            db.commit()
            db.refresh(plantilla)

            return plantilla

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def eliminar(
        cls,
        id_registro: int,
    ) -> None:

        db = SessionLocal()

        try:

            plantilla = (
                db.query(FacturaRecurrente)
                .filter(
                    FacturaRecurrente.id == id_registro,
                )
                .first()
            )

            if plantilla is not None:

                db.delete(plantilla)
                db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def generar_una(
        cls,
        id_registro: int,
    ):

        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        db = SessionLocal()

        try:

            plantilla = (
                db.query(FacturaRecurrente)
                .filter(
                    FacturaRecurrente.id == id_registro,
                )
                .first()
            )

            if plantilla is None:

                raise ValueError(
                    "Plantilla no encontrada.",
                )

            if not plantilla.activa:

                raise ValueError(
                    "Esta plantilla está inactiva.",
                )

            detalles = (
                db.query(FacturaRecurrenteDetalle)
                .filter(
                    FacturaRecurrenteDetalle.plantilla_id
                    == plantilla.id,
                )
                .order_by(
                    FacturaRecurrenteDetalle.orden,
                )
                .all()
            )

            lineas = [
                {
                    "producto_id": detalle.producto_id,
                    "descripcion": detalle.descripcion,
                    "cantidad": float(
                        detalle.cantidad or 1,
                    ),
                    "precio_unitario": float(
                        detalle.precio_unitario or 0,
                    ),
                    "impuesto_id": detalle.impuesto_id,
                    "precio_incluye_iva": (
                        detalle.precio_incluye_iva
                    ),
                }
                for detalle in detalles
            ]

            cliente_id = plantilla.cliente_id
            proxima = plantilla.proxima_fecha
            periodicidad = plantilla.periodicidad

        finally:

            db.close()

        factura = ServicioFacturaVenta.guardar_completa(
            {
                "cliente_id": cliente_id,
                "fecha": date.today(),
                "observaciones": (
                    f"Generada automáticamente desde la "
                    f"plantilla recurrente '{plantilla.nombre}'."
                ),
            },
            lineas,
        )

        db = SessionLocal()

        try:

            plantilla = (
                db.query(FacturaRecurrente)
                .filter(
                    FacturaRecurrente.id == id_registro,
                )
                .first()
            )

            plantilla.ultima_generada_en = date.today()
            plantilla.facturas_generadas = (
                (plantilla.facturas_generadas or 0) + 1
            )
            plantilla.proxima_fecha = (
                calcular_proxima_fecha(
                    proxima,
                    periodicidad,
                )
            )

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

        return factura

    @classmethod
    def generar_pendientes(
        cls,
        *,
        referencia: date | None = None,
    ) -> dict:

        hoy = referencia or date.today()

        db = SessionLocal()

        try:

            ids_pendientes = [
                plantilla.id
                for plantilla in (
                    db.query(FacturaRecurrente)
                    .filter(
                        FacturaRecurrente.activa.is_(
                            True,
                        ),
                        FacturaRecurrente.proxima_fecha
                        <= hoy,
                    )
                    .all()
                )
            ]

        finally:

            db.close()

        generadas = 0
        errores: list[tuple[int, str]] = []

        for plantilla_id in ids_pendientes:

            try:

                cls.generar_una(plantilla_id)

                generadas += 1

            except ValueError as error:

                errores.append(
                    (plantilla_id, str(error)),
                )

        return {
            "generadas": generadas,
            "errores": errores,
        }
