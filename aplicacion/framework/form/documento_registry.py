from __future__ import annotations

from aplicacion.dominio.documentos import consulta


class DocumentoRegistry:
    """
    Registro de procesadores de documentos (delegado a dominio).
    """

    @classmethod
    def registrar(
        cls,
        processor,
    ):
        consulta.registrar(
            processor,
        )

    @classmethod
    def obtener(cls):
        return consulta.obtener_procesador()
