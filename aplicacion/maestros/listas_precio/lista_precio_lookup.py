from __future__ import annotations

from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)
from aplicacion.framework.lookup.lookup_result import (
    LookupResult,
)

from .datasource import ListaPrecioDataSource


class ListaPrecioLookup(LookupDataSource):

    datasource = ListaPrecioDataSource

    campo_texto = "nombre"

    campo_codigo = "codigo"

    def buscar(
        self,
        texto: str = "",
    ) -> list[LookupResult]:

        items = []

        for registro in self.datasource.listar().registros:

            if not registro.activo:

                continue

            descripcion = str(
                registro.nombre
                or "",
            )

            if texto:

                busqueda = texto.lower()

                if (
                    busqueda
                    not in descripcion.lower()
                    and busqueda
                    not in str(
                        registro.codigo
                        or "",
                    ).lower()
                ):

                    continue

            items.append(

                LookupResult(

                    valor=registro.id,

                    codigo=str(
                        registro.codigo
                        or "",
                    ),

                    texto=descripcion,

                    objeto=registro,

                )

            )

        return items
