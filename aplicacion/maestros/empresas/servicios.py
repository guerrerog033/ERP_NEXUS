from __future__ import annotations

import shutil
from pathlib import Path

from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.maestros.empresas.repositorio import EmpresaRepositorio

RUTA_LOGOS = (
    Path(__file__)
    .resolve()
    .parents[2]
    / "recursos"
    / "imagenes"
    / "empresa"
)


class EmpresaServicio(ServicioBase):

    repositorio = EmpresaRepositorio

    @classmethod
    def validar(cls, datos, id_registro=None):

        nit = datos["nit"].strip()

        if not nit:
            raise Exception(
                "El NIT es obligatorio."
            )

        razon = datos["razon_social"].strip()

        if not razon:
            raise Exception(
                "La razón social es obligatoria."
            )

        empresa = cls.repositorio.obtener_por_nit(
            nit
        )

        # Nuevo registro
        if id_registro is None:

            if empresa is not None:

                raise Exception(
                    "Ya existe una empresa con ese NIT."
                )

        # Edición

        elif (
            empresa is not None
            and empresa.id != id_registro
        ):

            raise Exception(
                "Ya existe otra empresa con ese NIT."
            )

        archivo_logo = datos.pop(
            "_logo_archivo",
            None,
        )

        if archivo_logo:

            datos["logo_ruta"] = cls._guardar_logo(
                archivo_logo,
                nit,
                datos.get("logo_ruta"),
            )

        datos.pop(
            "_logo_archivo",
            None,
        )

    @classmethod
    def _guardar_logo(
        cls,
        archivo_origen: str,
        nit: str,
        logo_actual: str | None = None,
    ) -> str:

        origen = Path(archivo_origen)

        if not origen.is_file():

            return logo_actual or ""

        RUTA_LOGOS.mkdir(
            parents=True,
            exist_ok=True,
        )

        extension = origen.suffix.lower() or ".png"

        identificador = "".join(
            caracter
            for caracter in nit
            if caracter.isalnum()
        ) or "empresa"

        nombre = f"{identificador}{extension}"

        destino = RUTA_LOGOS / nombre

        shutil.copy2(
            origen,
            destino,
        )

        return f"empresa/{nombre}"

    @classmethod
    def ruta_logo_absoluta(
        cls,
        ruta_relativa: str | None,
    ) -> Path | None:

        if not ruta_relativa:

            return None

        texto = str(
            ruta_relativa,
        ).strip().replace(
            "\\",
            "/",
        )

        if not texto:

            return None

        base = (
            Path(__file__)
            .resolve()
            .parents[2]
            / "recursos"
            / "imagenes"
        )

        nombre = Path(
            texto,
        ).name

        candidatos = (
            Path(texto),
            Path(texto).expanduser(),
            base / texto,
            RUTA_LOGOS / nombre,
            RUTA_LOGOS / texto,
        )

        vistos: set[str] = set()

        for ruta in candidatos:

            try:

                ruta_resuelta = ruta.resolve()

            except OSError:

                continue

            clave = str(
                ruta_resuelta,
            ).lower()

            if (
                clave in vistos
                or not ruta_resuelta.is_file()
            ):

                continue

            vistos.add(
                clave,
            )

            return ruta_resuelta

        return None