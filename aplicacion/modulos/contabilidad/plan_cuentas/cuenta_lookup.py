from __future__ import annotations

from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)
from aplicacion.framework.lookup.lookup_result import (
    LookupResult,
)

from .servicios import ServicioPlanCuenta


class PlanCuentaLookup(LookupDataSource):

    campo_texto = "nombre"

    campo_codigo = "codigo"

    def __init__(
        self,
    ) -> None:
        # Busca directamente en el servicio (ver ``buscar``); no usa
        # el datasource genérico. Antes la base exigía uno y el Libro
        # mayor fallaba al abrir con "Debe definir datasource".
        pass

    def buscar(
        self,
        texto: str = "",
    ) -> list[LookupResult]:

        return ServicioPlanCuenta.buscar_para_lookup(
            texto.strip(),
        )
