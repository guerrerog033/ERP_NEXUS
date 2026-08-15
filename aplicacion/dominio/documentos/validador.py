class ValidadorDocumento:
    """Validaciones básicas de tipo/número de documento."""

    @staticmethod
    def validar(tipo, numero) -> bool:
        numero = str(numero).strip()

        if not numero:
            raise ValueError(
                "Debe ingresar un documento.",
            )

        _ = tipo
        return True
