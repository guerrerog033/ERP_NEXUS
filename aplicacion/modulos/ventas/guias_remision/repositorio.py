from __future__ import annotations

from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import (
    GuiaRemisionElectronica,
    GuiaRemisionElectronicaDetalle,
)


class RepositorioGuiaRemisionElectronica(RepositorioBase):

    modelo = GuiaRemisionElectronica

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()

            consulta = db.query(GuiaRemisionElectronica)

            if texto:

                consulta = consulta.filter(
                    GuiaRemisionElectronica.numero.ilike(
                        f"%{texto}%",
                    )
                    | GuiaRemisionElectronica.remision_numero.ilike(
                        f"%{texto}%",
                    )
                    | GuiaRemisionElectronica.cude.ilike(
                        f"%{texto}%",
                    )
                )

            return (
                consulta.order_by(
                    GuiaRemisionElectronica.fecha.desc(),
                    GuiaRemisionElectronica.numero.desc(),
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
                db.query(GuiaRemisionElectronica.numero)
                .filter(
                    GuiaRemisionElectronica.numero.like(
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
    def obtener_completa(
        cls,
        id_registro: int,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(GuiaRemisionElectronica)
                .options(
                    joinedload(
                        GuiaRemisionElectronica.detalles,
                    ),
                )
                .filter(
                    GuiaRemisionElectronica.id
                    == id_registro,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def obtener_por_remision(
        cls,
        remision_id: int,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(GuiaRemisionElectronica)
                .options(
                    joinedload(
                        GuiaRemisionElectronica.detalles,
                    ),
                )
                .filter(
                    GuiaRemisionElectronica.remision_id
                    == remision_id,
                    GuiaRemisionElectronica.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    GuiaRemisionElectronica.id.desc(),
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def guardar_completa(
        cls,
        cabecera: dict,
        lineas: list[dict],
    ):

        db = SessionLocal()

        try:

            registro = GuiaRemisionElectronica(
                **{
                    clave: cabecera[clave]
                    for clave in cabecera
                    if hasattr(
                        GuiaRemisionElectronica,
                        clave,
                    )
                },
            )

            db.add(registro)
            db.flush()

            for indice, linea in enumerate(
                lineas,
                start=1,
            ):

                detalle = GuiaRemisionElectronicaDetalle(
                    guia_id=registro.id,
                    producto_id=linea.get(
                        "producto_id",
                    ),
                    producto_variante_id=linea.get(
                        "producto_variante_id",
                    ),
                    descripcion=linea["descripcion"],
                    cantidad=linea["cantidad"],
                    precio_unitario=linea[
                        "precio_unitario"
                    ],
                    total_linea=linea["total_linea"],
                    orden=indice,
                )

                db.add(detalle)

            db.commit()
            db.refresh(registro)

            return cls.obtener_completa(
                registro.id,
            )

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_emision(
        cls,
        id_registro: int,
        *,
        cude: str,
        estado: str,
        estado_dian: str,
        mensaje_dian: str = "",
        ruta_xml: str = "",
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(GuiaRemisionElectronica)
                .filter(
                    GuiaRemisionElectronica.id
                    == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.cude = cude or None
            registro.estado = estado
            registro.estado_dian = estado_dian
            registro.mensaje_dian = mensaje_dian or None
            registro.ruta_xml = ruta_xml or None

            db.commit()
            db.refresh(registro)

            return registro

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
