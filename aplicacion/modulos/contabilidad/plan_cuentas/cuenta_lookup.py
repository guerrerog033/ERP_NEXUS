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

    def buscar(
        self,
        texto: str = "",
    ) -> list[LookupResult]:

        return ServicioPlanCuenta.buscar_para_lookup(
            texto.strip(),
        )
