from __future__ import annotations

from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)
from aplicacion.framework.lookup.lookup_result import (
    LookupResult,
)

from .datasource import TerceroDataSource


class ProveedorLookup(LookupDataSource):

    datasource = TerceroDataSource

    campo_texto = "razon_social"

    campo_codigo = "numero_documento"

    def buscar(
        self,
        texto: str = "",
    ) -> list[LookupResult]:

        items = []

        for registro in self.datasource.listar().registros:

            if registro.tipo_tercero != "Proveedor" and not getattr(
                registro,
                "es_proveedor",
                False,
            ):

                continue

            descripcion = str(
                getattr(
                    registro,
                    self.campo_texto,
                    "",
                )
                or registro.nombre_completo
                or "",
            )

            if texto:

                busqueda = texto.lower()

                coincidencias = [
                    descripcion.lower(),
                    str(
                        registro.numero_documento
                        or "",
                    ).lower(),
                ]

                if not any(
                    busqueda in valor
                    for valor in coincidencias
                ):

                    continue

            codigo = str(
                registro.numero_documento
                or "",
            )

            items.append(

                LookupResult(

                    valor=registro.id,

                    codigo=codigo,

                    texto=descripcion,

                    objeto=registro,

                )

            )

        return items
