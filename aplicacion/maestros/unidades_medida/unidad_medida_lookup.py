from __future__ import annotations

from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)

from .datasource import UnidadMedidaDataSource


class UnidadMedidaLookup(LookupDataSource):

    datasource = UnidadMedidaDataSource

    campo_texto = "nombre"

    campo_codigo = "codigo"
