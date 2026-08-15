"""Registro de vínculos entre documentos comerciales."""

from __future__ import annotations

from aplicacion.base_datos.conexion import SessionLocal

from .modelos import DocumentoVinculo


class DocumentoVinculoRepositorio:

    @classmethod
    def registrar(
        cls,
        tipo_origen: str,
        documento_origen_id: int,
        tipo_destino: str,
        documento_destino_id: int,
    ) -> DocumentoVinculo:

        db = SessionLocal()

        try:

            existente = (
                db.query(DocumentoVinculo)
                .filter(
                    DocumentoVinculo.tipo_origen
                    == tipo_origen,
                    DocumentoVinculo.documento_origen_id
                    == documento_origen_id,
                    DocumentoVinculo.tipo_destino
                    == tipo_destino,
                    DocumentoVinculo.documento_destino_id
                    == documento_destino_id,
                )
                .first()
            )

            if existente is not None:

                return existente

            vinculo = DocumentoVinculo(
                tipo_origen=tipo_origen,
                documento_origen_id=documento_origen_id,
                tipo_destino=tipo_destino,
                documento_destino_id=documento_destino_id,
            )

            db.add(vinculo)
            db.commit()
            db.refresh(vinculo)

            return vinculo

        finally:

            db.close()

    @classmethod
    def listar_por_documento(
        cls,
        tipo: str,
        documento_id: int,
    ) -> list[DocumentoVinculo]:

        db = SessionLocal()

        try:

            return (
                db.query(DocumentoVinculo)
                .filter(
                    (
                        (
                            DocumentoVinculo.tipo_origen
                            == tipo
                        )
                        & (
                            DocumentoVinculo.documento_origen_id
                            == documento_id
                        )
                    )
                    | (
                        (
                            DocumentoVinculo.tipo_destino
                            == tipo
                        )
                        & (
                            DocumentoVinculo.documento_destino_id
                            == documento_id
                        )
                    ),
                )
                .order_by(DocumentoVinculo.fecha_creacion)
                .all()
            )

        finally:

            db.close()
