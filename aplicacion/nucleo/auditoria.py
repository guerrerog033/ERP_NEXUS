from __future__ import annotations

from datetime import datetime
from pathlib import Path


class Auditoria:

    ARCHIVO = (
        Path(__file__).parent.parent.parent
        / "logs"
        / "auditoria.log"
    )

    @classmethod
    def _nombre_usuario(
        cls,
        usuario,
    ) -> str:

        if usuario is None:

            return "sistema"

        if isinstance(
            usuario,
            str,
        ):

            return usuario.strip() or "sistema"

        return str(
            getattr(
                usuario,
                "usuario",
                "sistema",
            )
            or "sistema",
        )

    @classmethod
    def registrar(
        cls,
        usuario,
        accion: str,
        detalle: str = "",
        *,
        modulo: str = "",
        entidad: str = "",
        entidad_id: int | None = None,
        exito: bool = True,
    ) -> None:

        nombre = cls._nombre_usuario(
            usuario,
        )

        fecha = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S",
        )

        partes_detalle = [
            detalle.strip(),
        ]

        if entidad:

            referencia = entidad

            if entidad_id is not None:

                referencia = (
                    f"{entidad}#{entidad_id}"
                )

            partes_detalle.append(
                referencia,
            )

        if modulo:

            partes_detalle.append(
                f"modulo={modulo}",
            )

        texto_detalle = " | ".join(
            parte
            for parte in partes_detalle
            if parte
        )

        estado = (
            "OK"
            if exito
            else "ERROR"
        )

        linea = (
            f"[{fecha}] "
            f"Usuario={nombre} | "
            f"Acción={accion} | "
            f"Estado={estado} | "
            f"{texto_detalle}\n"
        )

        cls.ARCHIVO.parent.mkdir(
            exist_ok=True,
        )

        with open(
            cls.ARCHIVO,
            "a",
            encoding="utf-8",
        ) as archivo:

            archivo.write(
                linea,
            )

        cls._registrar_bd(
            usuario=nombre,
            accion=accion,
            detalle=texto_detalle,
            modulo=modulo,
            entidad=entidad,
            entidad_id=entidad_id,
            exito=exito,
        )

    @classmethod
    def _registrar_bd(
        cls,
        *,
        usuario: str,
        accion: str,
        detalle: str,
        modulo: str,
        entidad: str,
        entidad_id: int | None,
        exito: bool,
    ) -> None:

        try:

            from aplicacion.base_datos.conexion import (
                SessionLocal,
            )

            from aplicacion.seguridad.modelos import (
                AuditoriaEvento,
            )

            db = SessionLocal()

            try:

                db.add(
                    AuditoriaEvento(
                        usuario=usuario,
                        accion=accion,
                        modulo=modulo or None,
                        entidad=entidad or None,
                        entidad_id=entidad_id,
                        detalle=detalle or None,
                        exito=bool(
                            exito,
                        ),
                    ),
                )

                db.commit()

            except Exception:

                db.rollback()

                raise

            finally:

                db.close()

        except Exception:

            pass

    @classmethod
    def registrar_sesion(
        cls,
        accion: str,
        detalle: str = "",
        *,
        modulo: str = "",
        entidad: str = "",
        entidad_id: int | None = None,
        exito: bool = True,
    ) -> None:

        from aplicacion.nucleo.sesion import (
            Sesion,
        )

        cls.registrar(
            Sesion.usuario(),
            accion,
            detalle,
            modulo=modulo,
            entidad=entidad,
            entidad_id=entidad_id,
            exito=exito,
        )
