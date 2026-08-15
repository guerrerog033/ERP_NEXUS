from __future__ import annotations

from aplicacion.maestros.impuestos.etiquetas import (
    etiqueta_impuesto,
)
from aplicacion.maestros.impuestos.repositorio import (
    RepositorioImpuesto,
)


# Tarifas Retefuente frecuentes (Colombia — Art. 383 E.T. y tablas DIAN)
RETENCIONES_RETEFUENTE = (
    {
        "codigo": "RF001",
        "nombre": "Retefuente 0.1% — pagos a terceros",
        "porcentaje": 0.1,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF050",
        "nombre": "Retefuente 0.5% — compras generales",
        "porcentaje": 0.5,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF100",
        "nombre": "Retefuente 1% — activos fijos / enajenación",
        "porcentaje": 1.0,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF150",
        "nombre": "Retefuente 1.5% — tarjetas débito/crédito",
        "porcentaje": 1.5,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF200",
        "nombre": "Retefuente 2% — contratos construcción",
        "porcentaje": 2.0,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF025",
        "nombre": "Retefuente 2.5% — compras declarantes",
        "porcentaje": 2.5,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF035",
        "nombre": "Retefuente 3.5% — compras no declarantes",
        "porcentaje": 3.5,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF035T",
        "nombre": "Retefuente 3.5% — transporte pasajeros",
        "porcentaje": 3.5,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF035A",
        "nombre": "Retefuente 3.5% — arrendamiento inmuebles",
        "porcentaje": 3.5,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF040",
        "nombre": "Retefuente 4% — servicios declarantes",
        "porcentaje": 4.0,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF040A",
        "nombre": "Retefuente 4% — arrendamiento muebles",
        "porcentaje": 4.0,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF060",
        "nombre": "Retefuente 6% — servicios no declarantes",
        "porcentaje": 6.0,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF070",
        "nombre": "Retefuente 7% — rendimientos financieros",
        "porcentaje": 7.0,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF100H",
        "nombre": "Retefuente 10% — honorarios no declarantes",
        "porcentaje": 10.0,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF110",
        "nombre": "Retefuente 11% — honorarios / comisiones",
        "porcentaje": 11.0,
        "tipo": "Retefuente",
    },
    {
        "codigo": "RF200",
        "nombre": "Retefuente 20% — regalías",
        "porcentaje": 20.0,
        "tipo": "Retefuente",
    },
)

# Tarifas ReteICA por municipio (referencia común; la base legal varía por acuerdo)
RETENCIONES_RETEICA = (
    {
        "codigo": "ICA207",
        "nombre": "ReteICA 2.0 — Medellín general",
        "porcentaje": 2.0,
        "tipo": "ReteICA",
    },
    {
        "codigo": "ICA414",
        "nombre": "ReteICA 4.14 — Bogotá industrial/comercio",
        "porcentaje": 4.14,
        "tipo": "ReteICA",
    },
    {
        "codigo": "ICA690",
        "nombre": "ReteICA 6.9 — Bogotá servicios varios",
        "porcentaje": 6.9,
        "tipo": "ReteICA",
    },
    {
        "codigo": "ICA700",
        "nombre": "ReteICA 7.0 — general",
        "porcentaje": 7.0,
        "tipo": "ReteICA",
    },
    {
        "codigo": "ICA800",
        "nombre": "ReteICA 8.0 — Cali servicios",
        "porcentaje": 8.0,
        "tipo": "ReteICA",
    },
    {
        "codigo": "ICA966",
        "nombre": "ReteICA 9.66 — Bogotá servicios",
        "porcentaje": 9.66,
        "tipo": "ReteICA",
    },
    {
        "codigo": "ICA1104",
        "nombre": "ReteICA 11.04 — Bogotá comercio",
        "porcentaje": 11.04,
        "tipo": "ReteICA",
    },
    {
        "codigo": "ICA1150",
        "nombre": "ReteICA 11.5 — Barranquilla",
        "porcentaje": 11.5,
        "tipo": "ReteICA",
    },
    {
        "codigo": "ICA1380",
        "nombre": "ReteICA 13.8 — Bogotá hoteles/restaurantes",
        "porcentaje": 13.8,
        "tipo": "ReteICA",
    },
)

# ReteIVA: porcentaje sobre el valor del IVA causado
RETENCIONES_RETEIVA = (
    {
        "codigo": "RIVA15",
        "nombre": "ReteIVA 15% — tarifa general",
        "porcentaje": 15.0,
        "tipo": "ReteIVA",
    },
    {
        "codigo": "RIVA100",
        "nombre": "ReteIVA 100% — casos especiales",
        "porcentaje": 100.0,
        "tipo": "ReteIVA",
    },
)

TODAS_RETENCIONES = (
    *RETENCIONES_RETEFUENTE,
    *RETENCIONES_RETEICA,
    *RETENCIONES_RETEIVA,
)

CODIGO_RETEIVA_PREDETERMINADO = "RIVA15"


def id_reteiva_predeterminado():

    impuesto = RepositorioImpuesto.obtener_por_codigo(
        CODIGO_RETEIVA_PREDETERMINADO,
    )

    if impuesto is None:

        return None

    return impuesto.id


def opciones_retencion_combo(
    tipo: str,
) -> list[tuple[str, int | None]]:

    tipo_normalizado = str(
        tipo or "",
    ).strip().upper()

    opciones: list[
        tuple[
            str,
            int | None,
        ]
    ] = [
        (
            "— Sin retención —",
            None,
        ),
    ]

    for datos in TODAS_RETENCIONES:

        if (
            str(
                datos.get(
                    "tipo",
                    "",
                )
                or "",
            ).upper()
            != tipo_normalizado
        ):

            continue

        impuesto = RepositorioImpuesto.obtener_por_codigo(
            str(
                datos["codigo"],
            ),
        )

        if impuesto is None:

            continue

        opciones.append(
            (
                etiqueta_impuesto(
                    impuesto,
                ),
                impuesto.id,
            ),
        )

    opciones[1:] = sorted(
        opciones[1:],
        key=lambda par: float(
            getattr(
                RepositorioImpuesto.obtener_por_id(
                    par[1],
                ),
                "porcentaje",
                0,
            )
            or 0,
        ),
    )

    return opciones
