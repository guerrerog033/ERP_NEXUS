from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DocumentoResult:
    """Resultado unificado de consulta de documento."""

    tipo: str = ""
    numero: str = ""
    dv: str = ""
    existe: bool = False

    razon_social: str = ""
    nombre_comercial: str = ""
    primer_nombre: str = ""
    segundo_nombre: str = ""
    primer_apellido: str = ""
    segundo_apellido: str = ""

    direccion: str = ""
    ciudad: str = ""
    departamento: str = ""
    pais: str = ""

    telefono: str = ""
    celular: str = ""
    correo: str = ""

    tercero: Any = None
    externo: Any = None

    origen: str = ""
    estado_rut: str = ""
    mensaje: str = ""
    error: str = ""

    @property
    def tipo_documento(self) -> str:
        return self.tipo

    @tipo_documento.setter
    def tipo_documento(self, value: str) -> None:
        self.tipo = value or ""

    @property
    def numero_documento(self) -> str:
        return self.numero

    @numero_documento.setter
    def numero_documento(self, value: str) -> None:
        self.numero = value or ""

    @property
    def encontrado(self) -> bool:
        return self.existe or self._tiene_datos()

    @property
    def ok(self) -> bool:
        return self.encontrado

    @property
    def tiene_tercero(self) -> bool:
        return self.tercero is not None

    def _tiene_datos(self) -> bool:
        return bool(
            self.razon_social
            or self.primer_nombre
            or self.primer_apellido
            or self.nombre_comercial
            or self.estado_rut
        )
