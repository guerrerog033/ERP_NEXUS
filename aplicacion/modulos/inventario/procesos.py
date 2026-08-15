from __future__ import annotations

PROCESOS_INVENTARIO: list[
    tuple[
        str,
        list[str],
    ]
] = [

    (
        "Maestros",
        [

            "Bodegas",

        ],
    ),

    (
        "Consultas",
        [

            "Kardex",

        ],
    ),

    (
        "Movimientos",
        [

            "Ajustes de inventario",

            "Traslados",

        ],
    ),

]

MODULOS_ENLACE: dict[
    str,
    str,
] = {

    "Bodegas": "Bodegas",

    "Kardex": "Kardex",

    "Ajustes de inventario": "AjustesInventario",

    "Traslados": "TrasladosInventario",

}
