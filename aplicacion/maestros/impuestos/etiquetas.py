from __future__ import annotations


def etiqueta_impuesto(
    impuesto,
) -> str:

    if impuesto is None:

        return ""

    tipo = str(
        getattr(
            impuesto,
            "tipo",
            "",
        )
        or "IVA",
    ).upper()

    porcentaje = float(
        getattr(
            impuesto,
            "porcentaje",
            0,
        )
        or 0,
    )

    if tipo == "IVA":

        if porcentaje <= 0:

            return "IVA 0%"

        return f"IVA {porcentaje:g}%"

    if tipo == "RETEFUENTE":

        if porcentaje <= 0:

            return "Retefuente"

        return f"RF {porcentaje:g}%"

    if tipo == "RETEICA":

        if porcentaje <= 0:

            return "ReteICA"

        return f"ICA {porcentaje:g}%"

    if tipo == "RETEIVA":

        if porcentaje <= 0:

            return "ReteIVA"

        return f"ReteIVA {porcentaje:g}%"

    nombre = str(
        getattr(
            impuesto,
            "nombre",
            "",
        )
        or "",
    ).strip()

    if nombre:

        return nombre

    return str(
        getattr(
            impuesto,
            "codigo",
            "",
        )
        or "",
    )


def etiqueta_impuesto_resultado(
    resultado,
) -> str:

    objeto = getattr(
        resultado,
        "objeto",
        None,
    )

    if objeto is not None:

        return etiqueta_impuesto(
            objeto,
        )

    return str(
        getattr(
            resultado,
            "texto",
            "",
        )
        or getattr(
            resultado,
            "codigo",
            "",
        )
        or "",
    )
