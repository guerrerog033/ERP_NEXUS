from __future__ import annotations

from aplicacion.framework.datasource import (
    SqlAlchemyDataSource,
)
from aplicacion.framework.lookup.lookup_datasource import (
    LookupDataSource,
)
from aplicacion.modulos.nomina.servicios import (
    ServicioNomina,
)


class ControladorPeriodoLookup:

    @classmethod
    def listar(cls):

        return ServicioNomina.listar_periodos()

    @classmethod
    def buscar(
        cls,
        texto,
    ):

        periodos = cls.listar()
        texto = str(texto or "").strip().lower()

        if not texto:

            return periodos

        return [
            periodo
            for periodo in periodos
            if texto
            in ServicioNomina.nombre_periodo(
                periodo,
            ).lower()
        ]


class PeriodoDataSource(SqlAlchemyDataSource):

    controlador = ControladorPeriodoLookup


class PeriodoLookup(LookupDataSource):

    datasource = PeriodoDataSource

    campo_texto = "nombre"
