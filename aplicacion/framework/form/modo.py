from __future__ import annotations

from enum import Enum


class ModoFormulario(str, Enum):
    NUEVO = "nuevo"
    EDICION = "edicion"
    CONSULTA = "consulta"


def resolver_modo(
    modo,
    id_registro=None,
) -> ModoFormulario:
    if modo is not None:
        if isinstance(
            modo,
            ModoFormulario,
        ):
            return modo

        return ModoFormulario(
            str(
                modo,
            ),
        )

    if id_registro is not None:
        return ModoFormulario.EDICION

    return ModoFormulario.NUEVO
