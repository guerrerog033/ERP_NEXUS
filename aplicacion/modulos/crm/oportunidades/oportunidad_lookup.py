from __future__ import annotations

from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)

from .datasource import OportunidadDataSource


class OportunidadLookup(LookupDataSource):

    datasource = OportunidadDataSource

    campo_texto = "titulo"

    campo_codigo = "codigo"
