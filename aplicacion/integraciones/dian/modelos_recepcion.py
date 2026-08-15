from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class ResultadoEnvioEvento:

    exito: bool = False
    mensaje: str = ""
    error: str = ""
    datos: dict = field(default_factory=dict)


@dataclass(slots=True)
class DocumentoRecibidoDian:

    track_id: str = ""
    cufe: str = ""
    numero: str = ""
    fecha: date | None = None
    nit_emisor: str = ""
    razon_social_emisor: str = ""
    total: float = 0.0
    datos: dict = field(default_factory=dict)


@dataclass(slots=True)
class ResultadoConexionRecepcion:

    exito: bool = False
    mensaje: str = ""
    error: str = ""


@dataclass(slots=True)
class ResultadoSincronizacionCompras:

    exito: bool = False
    importadas: int = 0
    omitidas: int = 0
    errores: list[str] = field(default_factory=list)
    mensaje: str = ""
    facturas_ids: list[int] = field(default_factory=list)
