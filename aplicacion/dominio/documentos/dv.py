from __future__ import annotations


class DVCalculator:
    """Calcula el dígito de verificación para NIT colombiano."""

    @staticmethod
    def calcular(numero) -> str:
        numero = "".join(c for c in str(numero) if c.isdigit())

        if not numero:
            return ""

        pesos = [
            71,
            67,
            59,
            53,
            47,
            43,
            41,
            37,
            29,
            23,
            19,
            17,
            13,
            7,
            3,
        ]

        numero = numero.zfill(15)

        suma = sum(
            int(digito) * peso
            for digito, peso in zip(numero, pesos)
        )

        residuo = suma % 11

        if residuo <= 1:
            return str(residuo)

        return str(11 - residuo)


CalculadoraDV = DVCalculator
