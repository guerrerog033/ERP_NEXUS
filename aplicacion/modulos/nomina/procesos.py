from __future__ import annotations

PROCESOS_NOMINA: list[
    tuple[
        str,
        list[str],
    ]
] = [

    (
        "Nómina",
        [

            "Empleados",

            "Contratos históricos",

            "Novedades",

            "Liquidación",

            "Prestaciones",

        ],
    ),

    (
        "Integraciones",
        [

            "Liquidación",

        ],
    ),

]

MODULOS_ENLACE: dict[
    str,
    str,
] = {

    "Empleados": "NominaEmpleados",

    "Contratos históricos": "NominaContratos",

    "Novedades": "NominaNovedades",

    "Liquidación": "NominaLiquidacion",

    "Prestaciones": "NominaPrestaciones",

}
