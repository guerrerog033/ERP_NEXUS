from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.nucleo.configuracion import Configuracion


class ServicioDocumentos:
    """Gestión documental por transacción."""

    @classmethod
    def carpeta_base(cls) -> Path:
        ruta = Configuracion.obtener(
            "documentos",
            "ruta",
            "aplicacion/recursos/documentos",
        )

        carpeta = Path(ruta)
        carpeta.mkdir(
            parents=True,
            exist_ok=True,
        )

        return carpeta

    @classmethod
    def adjuntar(
        cls,
        *,
        modulo: str,
        documento_id: int,
        ruta_origen: str | Path,
        tipo: str = "soporte",
        descripcion: str = "",
    ):
        from aplicacion.modulos.documentos.modelos import (
            DocumentoAdjunto,
        )

        origen = Path(ruta_origen)

        if not origen.exists():
            raise FileNotFoundError(
                str(origen),
            )

        destino_dir = (
            cls.carpeta_base()
            / modulo
            / str(documento_id)
        )
        destino_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        destino = destino_dir / origen.name
        shutil.copy2(
            origen,
            destino,
        )

        db = SessionLocal()

        try:
            registro = DocumentoAdjunto(
                modulo=modulo,
                documento_id=documento_id,
                tipo=tipo,
                nombre=origen.name,
                ruta=str(destino),
                descripcion=descripcion,
            )
            db.add(registro)
            db.commit()
            db.refresh(registro)

            return registro

        finally:
            db.close()

    @classmethod
    def listar(
        cls,
        *,
        modulo: str,
        documento_id: int,
    ) -> list:
        from aplicacion.modulos.documentos.modelos import (
            DocumentoAdjunto,
        )

        db = SessionLocal()

        try:
            return (
                db.query(DocumentoAdjunto)
                .filter(
                    DocumentoAdjunto.modulo == modulo,
                    DocumentoAdjunto.documento_id
                    == documento_id,
                )
                .order_by(
                    DocumentoAdjunto.fecha_creacion.desc(),
                )
                .all()
            )

        finally:
            db.close()
