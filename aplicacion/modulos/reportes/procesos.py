from __future__ import annotations

PROCESOS_REPORTES: list[
    tuple[
        str,
        list[str],
    ]
] = [

    (
        "Comercial",
        [

            "Panel gerencial",

            "Pipeline cotización → cobro",

        ],
    ),

    (
        "Operaciones",
        [

            "Ventas por periodo",

            "Compras por periodo",

            "Existencias de inventario",

        ],
    ),

    (
        "Financiero",
        [

            "Resumen de cartera",

            "Antigüedad de saldos",

            "Retenciones aplicadas",

            "Resumen de nómina",

        ],
    ),

    (
        "Tributario",
        [

            "Información exógena",

        ],
    ),

    (
        "Contabilidad",
        [

            "Libro mayor",

            "Balance de prueba",

        ],
    ),

]

MODULOS_ENLACE: dict[
    str,
    str,
] = {

    "Panel gerencial": "PanelGerencial",

    "Pipeline cotización → cobro": "ReportePipelineComercial",

    "Ventas por periodo": "ReporteVentas",

    "Compras por periodo": "ReporteCompras",

    "Existencias de inventario": "ReporteInventario",

    "Resumen de cartera": "ReporteCartera",

    "Antigüedad de saldos": "CarteraAntiguedad",

    "Retenciones aplicadas": "ReporteRetenciones",

    "Resumen de nómina": "ReporteNomina",

    "Información exógena": "InformacionExogena",

    "Libro mayor": "LibroMayor",

    "Balance de prueba": "BalancePrueba",

}
