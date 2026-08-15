from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class FiltroConsulta:
    """
    Filtro normalizado listo para aplicar en repositorio.
    """

    campo: str
    operador: str
    valor: Any


class FiltroBase:
    """
    Filtro declarativo de UI / consulta.
    """

    def __init__(
        self,
        campo: str,
        *,
        etiqueta: str = "",
    ):

        self.campo = campo
        self.etiqueta = etiqueta or campo.replace(
            "_",
            " ",
        ).title()

    def a_consulta(
        self,
        valor,
    ) -> FiltroConsulta | None:

        raise NotImplementedError


class TextFilter(
    FiltroBase,
):

    def a_consulta(
        self,
        valor,
    ) -> FiltroConsulta | None:

        texto = str(
            valor or "",
        ).strip()

        if not texto:

            return None

        return FiltroConsulta(
            campo=self.campo,
            operador="like",
            valor=f"%{texto}%",
        )


class ComboFilter(
    FiltroBase,
):

    def __init__(
        self,
        campo: str,
        *,
        etiqueta: str = "",
        opciones: list[tuple[str, str]] | None = None,
    ):

        super().__init__(
            campo,
            etiqueta=etiqueta,
        )

        self.opciones = list(
            opciones or [],
        )

    def a_consulta(
        self,
        valor,
    ) -> FiltroConsulta | None:

        if (
            valor is None
            or valor == ""
        ):

            return None

        return FiltroConsulta(
            campo=self.campo,
            operador="eq",
            valor=valor,
        )


class BooleanFilter(
    FiltroBase,
):

    def a_consulta(
        self,
        valor,
    ) -> FiltroConsulta | None:

        if valor is None:

            return None

        return FiltroConsulta(
            campo=self.campo,
            operador="eq",
            valor=bool(
                valor,
            ),
        )


class DateRangeFilter(
    FiltroBase,
):

    def a_consulta(
        self,
        valor,
    ) -> FiltroConsulta | None:

        return None

    def a_consultas(
        self,
        valor,
    ) -> list[FiltroConsulta]:

        if not isinstance(
            valor,
            dict,
        ):

            return []

        consultas: list[
            FiltroConsulta,
        ] = []

        desde = valor.get(
            "desde",
        )

        hasta = valor.get(
            "hasta",
        )

        if desde:

            consultas.append(
                FiltroConsulta(
                    campo=self.campo,
                    operador="gte",
                    valor=desde,
                ),
            )

        if hasta:

            consultas.append(
                FiltroConsulta(
                    campo=self.campo,
                    operador="lte",
                    valor=hasta,
                ),
            )

        return consultas


class LookupFilter(
    FiltroBase,
):

    def __init__(
        self,
        campo: str,
        *,
        etiqueta: str = "",
        placeholder: str = "Buscar…",
        lookup=None,
    ):

        super().__init__(
            campo,
            etiqueta=etiqueta,
        )

        self.placeholder = placeholder
        self.lookup = lookup

    def a_consulta(
        self,
        valor,
    ) -> FiltroConsulta | None:

        if valor is None or valor == "":

            return None

        if hasattr(
            valor,
            "valor",
        ):

            valor = valor.valor

        try:

            identificador = int(
                valor,
            )

        except (
            TypeError,
            ValueError,
        ):

            return None

        return FiltroConsulta(
            campo=self.campo,
            operador="eq",
            valor=identificador,
        )


def construir_filtros(
    definiciones: list[FiltroBase],
    valores: dict[str, Any],
) -> list[FiltroConsulta]:

    filtros: list[FiltroConsulta] = []

    for definicion in definiciones:

        valor = valores.get(
            definicion.campo,
        )

        if hasattr(
            definicion,
            "a_consultas",
        ):

            consultas = definicion.a_consultas(
                valor,
            )

            filtros.extend(
                consultas,
            )

            continue

        consulta = definicion.a_consulta(
            valor,
        )

        if consulta is not None:

            filtros.append(
                consulta,
            )

    return filtros
