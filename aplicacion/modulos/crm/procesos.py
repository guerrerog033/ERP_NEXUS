from __future__ import annotations

PROCESOS_CRM: list[
    tuple[
        str,
        list[str],
    ]
] = [

    (
        "Comercial",
        [

            "Oportunidades",

            "Actividades",

        ],
    ),

]

MODULOS_ENLACE: dict[
    str,
    str,
] = {

    "Oportunidades": "CRMOportunidades",

    "Actividades": "CRMActividades",

}
