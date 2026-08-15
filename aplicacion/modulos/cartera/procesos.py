from __future__ import annotations

PROCESOS_CARTERA: list[
    tuple[
        str,
        list[str],
    ]
] = [

    (
        "Cartera",
        [

            "Cuentas por cobrar",

            "Cuentas por pagar",

        ],
    ),

    (
        "Análisis",
        [

            "Antigüedad de saldos",

            "Estado de cuenta",

        ],
    ),

]

MODULOS_ENLACE: dict[
    str,
    str,
] = {

    "Cuentas por cobrar": "CarteraCxC",

    "Cuentas por pagar": "CarteraCxP",

    "Antigüedad de saldos": "CarteraAntiguedad",

    "Estado de cuenta": "CarteraEstadoCuenta",

}
