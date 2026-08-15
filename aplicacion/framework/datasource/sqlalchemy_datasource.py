from __future__ import annotations

from .datasource import DataSource
from .result import DataResult


class SqlAlchemyDataSource(DataSource):
    """
    Implementación base para DataSources
    que utilizan un controlador basado
    en SQLAlchemy.
    """

    controlador = None

    # ===============================================
    # Listar
    # ===============================================

    def listar(
        self,
        **kwargs,
    ):

        resultado = self.controlador.listar(
            **kwargs,
        )

        if isinstance(
            resultado,
            dict,
        ) and "registros" in resultado:

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

    # ===============================================
    # Buscar
    # ===============================================

    def buscar(
        self,
        texto,
        **kwargs,
    ):

        registros = self.controlador.buscar(
            texto,
            **kwargs,
        )

        if isinstance(
            registros,
            dict,
        ) and "registros" in registros:

            return DataResult(
                registros=registros[
                    "registros"
                ],
                total=registros.get(
                    "total",
                    0,
                ),
                pagina=registros.get(
                    "pagina",
                    1,
                ),
                por_pagina=registros.get(
                    "por_pagina",
                    0,
                ),
            )

        registros = list(
            registros or [],
        )

        return DataResult(
            registros=registros,
            total=len(
                registros,
            ),
            pagina=1,
            por_pagina=0,
        )

    # ===============================================
    # Obtener
    # ===============================================

    def obtener(
        self,
        id_registro,
    ):

        return self.controlador.obtener(
            id_registro
        )

    # ===============================================
    # Obtener por ID
    # ===============================================

    def obtener_por_id(
        self,
        id_registro,
    ):

        return self.obtener(
            id_registro
        )

    # ===============================================
    # Guardar
    # ===============================================

    def guardar(
        self,
        datos,
        id_registro=None,
    ):

        return self.controlador.guardar(
            datos,
            id_registro,
        )

    # ===============================================
    # Eliminar
    # ===============================================

    def eliminar(
        self,
        id_registro,
    ):

        return self.controlador.eliminar(
            id_registro,
        )
