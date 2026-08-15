from __future__ import annotations

from dataclasses import dataclass

from .text_field import TextField


@dataclass(slots=True)
class DocumentoField(TextField):
    """
    Campo especializado para documentos.

    Además del comportamiento de un TextField,
    conoce las reglas necesarias para:

        • Normalizar.
        • Calcular DV.
        • Buscar terceros.
        • Consultar fuentes externas.

    La lógica se implementará en el widget.
    """

    widget: str = "documento"

    calcular_dv: bool = True

    buscar_automaticamente: bool = True

    consultar_dian: bool = True

    consultar_rues: bool = True

    consultar_api: bool = True