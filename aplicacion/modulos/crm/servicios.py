from __future__ import annotations

from aplicacion.comunes.servicio_base import ServicioBase

from .repositorio import (
    RepositorioActividadCRM,
    RepositorioOportunidadCRM,
)


class ServicioOportunidadCRM(ServicioBase):

    repositorio = RepositorioOportunidadCRM

    entidad_auditoria = "OportunidadCRM"

    modulo_auditoria = "crm/oportunidades"

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):

        codigo = str(
            datos.get(
                "codigo",
                "",
            )
        ).strip().upper()

        titulo = str(
            datos.get(
                "titulo",
                "",
            )
        ).strip()

        cliente_id = int(
            datos.get(
                "cliente_id",
                0,
            )
            or 0,
        )

        valor_estimado = float(
            datos.get(
                "valor_estimado",
                0,
            )
            or 0,
        )

        if not codigo:

            raise ValueError(
                "El código de la oportunidad es obligatorio.",
            )

        if (
            RepositorioOportunidadCRM.existe_codigo(
                codigo,
                excluir_id=id_registro,
            )
        ):

            raise ValueError(
                "Ya existe una oportunidad con ese código.",
            )

        if not titulo:

            raise ValueError(
                "El título es obligatorio.",
            )

        if cliente_id <= 0:

            raise ValueError(
                "Seleccione un cliente.",
            )

        if valor_estimado < 0:

            raise ValueError(
                "El valor estimado no puede ser negativo.",
            )


class ServicioActividadCRM(ServicioBase):

    repositorio = RepositorioActividadCRM

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):

        oportunidad_id = int(
            datos.get(
                "oportunidad_id",
                0,
            )
            or 0,
        )

        titulo = str(
            datos.get(
                "titulo",
                "",
            )
        ).strip()

        fecha = datos.get(
            "fecha",
        )

        if oportunidad_id <= 0:

            raise ValueError(
                "Seleccione una oportunidad.",
            )

        if not titulo:

            raise ValueError(
                "El título es obligatorio.",
            )

        if fecha is None:

            raise ValueError(
                "Indique la fecha de la actividad.",
            )


class ServicioCRM:

    @classmethod
    def resumen(cls) -> dict[str, float | int]:

        return RepositorioOportunidadCRM.resumen()
