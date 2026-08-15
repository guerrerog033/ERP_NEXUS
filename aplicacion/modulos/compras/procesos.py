from __future__ import annotations

PROCESOS_COMPRAS: list[
    tuple[
        str,
        list[str],
    ]
] = [

    (
        "Documentos",
        [

            "Órdenes de compra",

            "Recepciones",

            "Facturas de compra",

            "Notas crédito compra",

            "Documentos soporte",

        ],
    ),

    (
        "Tesorería",
        [

            "Comprobantes de egreso",

        ],
    ),

]

MODULOS_ENLACE: dict[
    str,
    str,
] = {

    "Órdenes de compra": "OrdenesCompra",

    "Recepciones": "RecepcionesCompra",

    "Facturas de compra": "FacturasCompra",

    "Notas crédito compra": "NotasCreditoCompra",

    "Documentos soporte": "DocumentosSoporte",

    "Comprobantes de egreso": "ComprobantesEgreso",

}
