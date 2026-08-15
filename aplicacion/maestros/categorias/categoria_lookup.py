from __future__ import annotations

from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)

from .datasource import CategoriaDataSource


class CategoriaLookup(LookupDataSource):

    datasource = CategoriaDataSource

    campo_texto = "nombre"

    campo_codigo = "codigo"
