from __future__ import annotations

from .repositorio import RepositorioRemision
from .servicios import ServicioRemision


class IntegracionRemision:

    @classmethod
    def confirmar_remision(
        cls,
        id_registro: int,
    ):

        remision = ServicioRemision.obtener_completa(
            id_registro,
        )

        if remision is None:

            raise ValueError(
                "No se encontró la remisión.",
            )

        if remision.estado != "borrador":

            raise ValueError(
                "La remisión ya fue confirmada.",
            )

        RepositorioRemision.actualizar_estado_confirmacion(
            id_registro,
            estado="pendiente",
        )

        return ServicioRemision.obtener_completa(
            id_registro,
        )
