from __future__ import annotations

from abc import ABC

from .lookup_result import LookupResult


class LookupDataSource(ABC):
    """
    Clase base para cualquier Lookup del ERP.
    """

    datasource = None

    campo_valor = "id"

    campo_codigo = ""

    campo_texto = ""


    # =====================================================
    # Inicialización
    # =====================================================

    def __init__(self):

        if self.datasource is None:

            raise RuntimeError(
                "Debe definir datasource."
            )

        self.datasource = self.datasource()


    # =====================================================
    # Buscar
    # =====================================================

    def buscar(
        self,
        texto: str = "",
    ) -> list[LookupResult]:

        resultado = self.datasource.listar()

        items = []

        for registro in resultado.registros:

            descripcion = str(
                getattr(
                    registro,
                    self.campo_texto,
                )
            )

            if texto:

                if texto.lower() not in descripcion.lower():

                    continue

            codigo = ""

            if self.campo_codigo:

                codigo = getattr(
                    registro,
                    self.campo_codigo,
                )

            items.append(

                LookupResult(

                    valor=getattr(
                        registro,
                        self.campo_valor,
                    ),

                    codigo=codigo,

                    texto=descripcion,

                    objeto=registro,

                )

            )

        return items


    # =====================================================
    # Buscar por ID
    # =====================================================

    def buscar_por_id(
        self,
        valor,
    ) -> LookupResult | None:

        if valor is None:

            return None

        for resultado in self.buscar():

            if resultado.valor == valor:

                return resultado

        return None