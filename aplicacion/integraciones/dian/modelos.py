from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ResultadoDian:
    """
    Resultado normalizado de una consulta pública DIAN/RUES.
    No requiere certificado digital ni software habilitado.
    """

    encontrado: bool = False
    origen: str = ""

    tipo_documento: str = ""
    numero_documento: str = ""
    dv: str = ""

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
    correo: str = ""

    estado_rut: str = ""
    actividad_economica: str = ""
    mensaje: str = ""
    error: str = ""

    datos_crudos: dict = field(default_factory=dict)
