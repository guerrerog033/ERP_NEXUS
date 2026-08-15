from __future__ import annotations

from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)
from aplicacion.framework.lookup.lookup_result import (
    LookupResult,
)

from .datasource import ImpuestoDataSource
from .etiquetas import etiqueta_impuesto


class ImpuestoLookup(LookupDataSource):

    datasource = ImpuestoDataSource

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

            descripcion = etiqueta_impuesto(
                registro,
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
                    and busqueda
                    not in str(
                        registro.nombre
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
