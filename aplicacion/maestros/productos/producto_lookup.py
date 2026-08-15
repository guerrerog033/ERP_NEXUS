from __future__ import annotations

from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)
from aplicacion.framework.lookup.lookup_result import (
    LookupResult,
)

from .datasource import ProductoDataSource
from .servicios import ServicioProducto


class ProductoLookup(LookupDataSource):

    datasource = ProductoDataSource

    campo_texto = "nombre"

    campo_codigo = "codigo"

    def buscar(
        self,
        texto: str = "",
    ) -> list[LookupResult]:

        return ServicioProducto.buscar_para_lookup(
            texto.strip(),
        )
