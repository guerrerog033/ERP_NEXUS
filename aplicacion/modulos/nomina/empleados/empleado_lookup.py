from __future__ import annotations

from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)

from .datasource import EmpleadoDataSource


class EmpleadoLookup(LookupDataSource):

    datasource = EmpleadoDataSource

    campo_texto = "nombre_completo"

    campo_codigo = "codigo"
