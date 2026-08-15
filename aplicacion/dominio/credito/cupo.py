from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResultadoCupo:
    permitido: bool
    cupo: float
    utilizado: float
    disponible: float
    mensaje: str = ""


def evaluar_cupo(
    cupo_credito,
    cartera_pendiente,
    monto_operacion,
) -> ResultadoCupo:
    """
    Evalúa si una operación a crédito cabe en el cupo del tercero.
    Cupo <= 0 significa sin límite configurado.
    """

    cupo = float(
        cupo_credito or 0,
    )

    utilizado = float(
        cartera_pendiente or 0,
    )

    monto = float(
        monto_operacion or 0,
    )

    if cupo <= 0:
        return ResultadoCupo(
            permitido=True,
            cupo=0.0,
            utilizado=utilizado,
            disponible=0.0,
            mensaje="",
        )

    disponible = round(
        cupo - utilizado,
        2,
    )

    if monto > disponible:
        return ResultadoCupo(
            permitido=False,
            cupo=cupo,
            utilizado=utilizado,
            disponible=max(
                disponible,
                0.0,
            ),
            mensaje=(
                f"Cupo de crédito excedido. "
                f"Disponible: {max(disponible, 0.0):,.2f}."
            ),
        )

    return ResultadoCupo(
        permitido=True,
        cupo=cupo,
        utilizado=utilizado,
        disponible=disponible,
        mensaje="",
    )
