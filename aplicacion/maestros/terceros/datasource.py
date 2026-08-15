from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)
from aplicacion.framework.datasource.result import DataResult

from .controlador import TerceroControlador
from .servicio import TerceroServicio


class TerceroDataSource(SqlAlchemyDataSource):

    controlador = TerceroControlador

    tipo_filtro = None

    def _parametros_tipo(
        self,
        kwargs: dict,
    ) -> dict:

        parametros = dict(
            kwargs,
        )

        if self.tipo_filtro:

            parametros["tipo_tercero"] = (
                self.tipo_filtro
            )

        return parametros

    def listar(
        self,
        **kwargs,
    ):

        parametros = self._parametros_tipo(
            kwargs,
        )

        resultado = TerceroServicio.listar(
            **parametros,
        )

        if isinstance(
            resultado,
            dict,
        ):

            return DataResult(
                registros=resultado[
                    "registros"
                ],
                total=resultado.get(
                    "total",
                    0,
                ),
                pagina=resultado.get(
                    "pagina",
                    kwargs.get(
                        "pagina",
                        1,
                    ),
                ),
                por_pagina=resultado.get(
                    "por_pagina",
                    kwargs.get(
                        "por_pagina",
                        0,
                    ),
                ),
            )

        registros = list(
            resultado or [],
        )

        return DataResult(
            registros=registros,
            total=len(
                registros,
            ),
            pagina=kwargs.get(
                "pagina",
                1,
            ),
            por_pagina=kwargs.get(
                "por_pagina",
                0,
            ),
        )

    def buscar(
        self,
        texto,
        **kwargs,
    ):

        parametros = self._parametros_tipo(
            kwargs,
        )

        resultado = TerceroServicio.buscar(
            texto,
            **parametros,
        )

        if isinstance(
            resultado,
            dict,
        ):

            return DataResult(
                registros=resultado[
                    "registros"
                ],
                total=resultado.get(
                    "total",
                    0,
                ),
                pagina=resultado.get(
                    "pagina",
                    kwargs.get(
                        "pagina",
                        1,
                    ),
                ),
                por_pagina=resultado.get(
                    "por_pagina",
                    kwargs.get(
                        "por_pagina",
                        0,
                    ),
                ),
            )

        registros = list(
            resultado or [],
        )

        return DataResult(
            registros=registros,
            total=len(
                registros,
            ),
            pagina=1,
            por_pagina=0,
        )

    def documento_changed(
        self,
        tipo_documento,
        numero_documento,
    ):

        return self.controlador.documento_changed(

            tipo_documento,

            numero_documento,

        )


class ClienteDataSource(TerceroDataSource):

    tipo_filtro = "Cliente"


class ProveedorDataSource(TerceroDataSource):

    tipo_filtro = "Proveedor"


class OtroDataSource(TerceroDataSource):

    tipo_filtro = "Otro"
