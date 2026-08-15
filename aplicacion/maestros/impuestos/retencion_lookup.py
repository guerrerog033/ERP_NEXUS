from __future__ import annotations

from aplicacion.framework.lookup.lookup_result import (
    LookupResult,
)

from .etiquetas import etiqueta_impuesto
from .impuesto_lookup import ImpuestoLookup
from .repositorio import RepositorioImpuesto
from .servicios import ServicioImpuesto


class _RetencionLookupBase(ImpuestoLookup):

    tipo_retencion = ""

    def buscar(
        self,
        texto: str = "",
    ) -> list[LookupResult]:

        items = []

        registros = ServicioImpuesto.buscar(
            texto.strip(),
        )

        for registro in registros:

            if not registro.activo:

                continue

            if (
                str(
                    registro.tipo
                    or "",
                ).strip().upper()
                != self.tipo_retencion.upper()
            ):

                continue

            items.append(

                LookupResult(

                    valor=registro.id,

                    codigo=str(
                        registro.codigo
                        or "",
                    ),

                    texto=etiqueta_impuesto(
                        registro,
                    ),

                    objeto=registro,

                )

            )

        return items

    def buscar_por_id(
        self,
        valor,
    ) -> LookupResult | None:

        if valor is None:

            return None

        registro = RepositorioImpuesto.obtener_por_id(
            valor,
        )

        if (
            registro is None
            or not registro.activo
        ):

            return None

        if (
            str(
                registro.tipo
                or "",
            ).strip().upper()
            != self.tipo_retencion.upper()
        ):

            return None

        return LookupResult(

            valor=registro.id,

            codigo=str(
                registro.codigo
                or "",
            ),

            texto=etiqueta_impuesto(
                registro,
            ),

            objeto=registro,

        )


class RetefuenteLookup(_RetencionLookupBase):

    tipo_retencion = "Retefuente"


class ReteICALookup(_RetencionLookupBase):

    tipo_retencion = "ReteICA"


class ReteIVALookup(_RetencionLookupBase):

    tipo_retencion = "ReteIVA"
