from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LookupResult:
    """
    Resultado devuelto por un Lookup.

    Contiene la información necesaria para que
    cualquier formulario pueda trabajar sin
    conocer el modelo original.
    """

    valor: object

    texto: str

    codigo: str = ""

    objeto: object | None = None

    producto_variante_id: int | None = None