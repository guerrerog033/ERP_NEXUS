from __future__ import annotations

from typing import Any


def _serializar_valor(
    valor: Any,
) -> str | None:

    if valor is None:

        return None

    return str(
        valor,
    )


class AuditoriaCampos:

    @classmethod
    def registrar_cambios(
        cls,
        *,
        usuario,
        entidad: str,
        entidad_id: int,
        cambios: dict[
            str,
            tuple[Any, Any],
        ],
        modulo: str = "",
    ) -> None:

        if not cambios:

            return

        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )

        from aplicacion.nucleo.auditoria import (
            Auditoria,
        )

        from aplicacion.seguridad.modelos import (
            AuditoriaCampo,
        )

        nombre = Auditoria._nombre_usuario(
            usuario,
        )

        db = SessionLocal()

        try:

            for campo, (
                anterior,
                nuevo,
            ) in cambios.items():

                texto_anterior = _serializar_valor(
                    anterior,
                )

                texto_nuevo = _serializar_valor(
                    nuevo,
                )

                if (
                    texto_anterior
                    == texto_nuevo
                ):

                    continue

                db.add(
                    AuditoriaCampo(
                        usuario=nombre,
                        modulo=modulo
                        or None,
                        entidad=entidad,
                        entidad_id=entidad_id,
                        campo=campo,
                        valor_anterior=texto_anterior,
                        valor_nuevo=texto_nuevo,
                    ),
                )

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def detectar_cambios(
        cls,
        registro,
        datos: dict,
        *,
        campos: list[str] | None = None,
    ) -> dict[
        str,
        tuple[Any, Any],
    ]:

        cambios: dict[
            str,
            tuple[Any, Any],
        ] = {}

        nombres = campos or list(
            datos.keys(),
        )

        for nombre in nombres:

            if nombre not in datos:

                continue

            anterior = getattr(
                registro,
                nombre,
                None,
            )

            nuevo = datos.get(
                nombre,
            )

            if (
                _serializar_valor(
                    anterior,
                )
                != _serializar_valor(
                    nuevo,
                )
            ):

                cambios[
                    nombre
                ] = (
                    anterior,
                    nuevo,
                )

        return cambios
