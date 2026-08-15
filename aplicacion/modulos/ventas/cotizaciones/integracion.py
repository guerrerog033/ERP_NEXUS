from __future__ import annotations

from .repositorio import RepositorioCotizacion
from .servicios import ServicioCotizacion


class IntegracionCotizacion:

    @classmethod
    def confirmar_cotizacion(
        cls,
        id_registro: int,
    ):

        cotizacion = ServicioCotizacion.obtener_completa(
            id_registro,
        )

        if cotizacion is None:

            raise ValueError(
                "No se encontró la cotización.",
            )

        if cotizacion.estado != "borrador":

            raise ValueError(
                "La cotización ya fue confirmada.",
            )

        RepositorioCotizacion.actualizar_estado_confirmacion(
            id_registro,
            estado="aprobada",
        )

        return ServicioCotizacion.obtener_completa(
            id_registro,
        )
