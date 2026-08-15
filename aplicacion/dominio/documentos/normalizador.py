class NormalizadorDocumento:
    """Normaliza números de documento (solo alfanuméricos, mayúsculas)."""

    @staticmethod
    def normalizar(numero) -> str:
        return "".join(
            c
            for c in str(numero)
            if c.isalnum()
        ).upper()
