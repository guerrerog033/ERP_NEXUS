from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import DocumentoSoporte, DocumentoSoporteDetalle


class RepositorioDocumentoSoporte(RepositorioBase):

    modelo = DocumentoSoporte

    @classmethod
    def buscar(cls, texto):

        db = SessionLocal()

        try:

            texto = texto.strip()
            consulta = db.query(DocumentoSoporte)

            if texto:

                consulta = consulta.filter(
                    DocumentoSoporte.numero.ilike(
                        f"%{texto}%",
                    )
                    | DocumentoSoporte.cuds.ilike(
                        f"%{texto}%",
                    )
                    | DocumentoSoporte.razon_social_proveedor.ilike(
                        f"%{texto}%",
                    )
                )

            return (
                consulta.order_by(
                    DocumentoSoporte.fecha.desc(),
                    DocumentoSoporte.numero.desc(),
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def existe_numero(
        cls,
        numero,
        excluir_id=None,
    ):

        db = SessionLocal()

        try:

            consulta = (
                db.query(DocumentoSoporte)
                .filter(
                    DocumentoSoporte.numero == numero,
                )
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    DocumentoSoporte.id != excluir_id,
                )

            return consulta.first() is not None

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
                db.query(DocumentoSoporte.numero)
                .filter(
                    DocumentoSoporte.numero.like(
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
        id_registro,
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(DocumentoSoporte)
                .options(
                    joinedload(
                        DocumentoSoporte.detalles,
                    ),
                )
                .filter(
                    DocumentoSoporte.id == id_registro,
                )
                .first()
            )

            if registro is not None:

                list(
                    registro.detalles,
                )

            return registro

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

            registro = DocumentoSoporte(
                **cabecera,
            )

            db.add(registro)
            db.flush()

            for indice, linea in enumerate(lineas):

                detalle = DocumentoSoporteDetalle(
                    documento_id=registro.id,
                    descripcion=linea["descripcion"],
                    cantidad=linea["cantidad"],
                    precio_unitario=linea[
                        "precio_unitario"
                    ],
                    impuesto_id=linea.get(
                        "impuesto_id",
                    ),
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
    def actualizar_completa(
        cls,
        id_registro,
        cabecera: dict,
        lineas: list[dict],
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(DocumentoSoporte)
                .filter(
                    DocumentoSoporte.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            for campo, valor in cabecera.items():

                setattr(
                    registro,
                    campo,
                    valor,
                )

            (
                db.query(DocumentoSoporteDetalle)
                .filter(
                    DocumentoSoporteDetalle.documento_id
                    == id_registro,
                )
                .delete()
            )

            for indice, linea in enumerate(lineas):

                detalle = DocumentoSoporteDetalle(
                    documento_id=id_registro,
                    descripcion=linea["descripcion"],
                    cantidad=linea["cantidad"],
                    precio_unitario=linea[
                        "precio_unitario"
                    ],
                    impuesto_id=linea.get(
                        "impuesto_id",
                    ),
                    total_linea=linea["total_linea"],
                    orden=indice,
                )

                db.add(detalle)

            db.commit()

            return cls.obtener_completa(
                id_registro,
            )

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def actualizar_emision(
        cls,
        id_registro,
        *,
        cuds: str,
        estado: str,
        estado_dian: str,
        mensaje_dian: str = "",
        ruta_xml: str = "",
    ):

        db = SessionLocal()

        try:

            registro = (
                db.query(DocumentoSoporte)
                .filter(
                    DocumentoSoporte.id == id_registro,
                )
                .first()
            )

            if registro is None:

                return None

            registro.cuds = cuds or None
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
