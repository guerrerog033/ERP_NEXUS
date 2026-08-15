from __future__ import annotations

from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)

from .datasource import MarcaDataSource


class MarcaLookup(LookupDataSource):

    datasource = MarcaDataSource

    campo_texto = "nombre"

    campo_codigo = "codigo"
