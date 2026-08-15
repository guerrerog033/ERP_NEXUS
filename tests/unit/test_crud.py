from aplicacion.comunes.repositorio_base import RepositorioBase
from aplicacion.framework.datagrid.filtros import (
    BooleanFilter,
    ComboFilter,
    TextFilter,
    construir_filtros,
)
from aplicacion.framework.datasource.result import DataResult
from aplicacion.framework.datasource.sqlalchemy_datasource import (
    SqlAlchemyDataSource,
)


class _ControladorPrueba:

    @classmethod
    def listar(
        cls,
        **kwargs,
    ):

        if kwargs.get(
            "pagina",
        ):

            return {
                "registros": [
                    {"id": 1},
                ],
                "total": 120,
                "pagina": kwargs[
                    "pagina"
                ],
                "por_pagina": kwargs[
                    "por_pagina"
                ],
            }

        return [
            {"id": 1},
            {"id": 2},
        ]


class _DataSourcePrueba(
    SqlAlchemyDataSource,
):

    controlador = _ControladorPrueba


def test_sqlalchemy_datasource_paginacion():
    ds = _DataSourcePrueba()

    resultado = ds.listar(
        pagina=2,
        por_pagina=50,
    )

    assert isinstance(
        resultado,
        DataResult,
    )
    assert resultado.total == 120
    assert resultado.pagina == 2
    assert resultado.por_pagina == 50
    assert len(
        resultado.registros,
    ) == 1


def test_sqlalchemy_datasource_lista_simple():
    ds = _DataSourcePrueba()

    resultado = ds.listar()

    assert resultado.total == 2
    assert len(
        resultado.registros,
    ) == 2


def test_filtros_declarativos():
    definiciones = [
        TextFilter(
            "numero_documento",
        ),
        ComboFilter(
            "tipo_documento",
        ),
        BooleanFilter(
            "activo",
        ),
    ]

    filtros = construir_filtros(
        definiciones,
        {
            "numero_documento": "900",
            "tipo_documento": "NIT",
            "activo": True,
        },
    )

    assert len(
        filtros,
    ) == 3

    assert filtros[0].operador == "like"
    assert filtros[1].operador == "eq"


def test_repositorio_aplicar_filtro_eq():
    class _Modelo:

        activo = "activo_col"

    class _Repo(
        RepositorioBase,
    ):

        modelo = _Modelo

    class _Consulta:

        def __init__(
            self,
        ):

            self.filtros = []

        def filter(
            self,
            *args,
            **kwargs,
        ):

            self.filtros.append(
                args,
            )

            return self

    consulta = _Consulta()

    from aplicacion.framework.datagrid.filtros import (
        FiltroConsulta,
    )

    consulta = _Repo._aplicar_filtro(
        consulta,
        FiltroConsulta(
            campo="activo",
            operador="eq",
            valor=True,
        ),
    )

    assert consulta.filtros
