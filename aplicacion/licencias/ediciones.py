from __future__ import annotations

EDICIONES: dict[str, dict] = {

    "trial": {

        "codigo_serial": "TR",

        "nombre": "Prueba",

        "modulos": ["*"],

        "max_usuarios": 2,

        "dias_predeterminados": 30,

    },

    "starter": {

        "codigo_serial": "ST",

        "nombre": "Starter",

        "modulos": [

            "Productos",

            "Categorías",

            "Marcas",

            "Clientes",

            "Cotizaciones",

        ],

        "max_usuarios": 3,

        "dias_predeterminados": 365,

    },

    "profesional": {

        "codigo_serial": "PR",

        "nombre": "Profesional",

        "modulos": [

            "Productos",

            "Categorías",

            "Marcas",

            "Clientes",

            "Proveedores",

            "Cotizaciones",

            "Pedidos",

            "FacturasVenta",

            "NotasCreditoVenta",

            "NotasDebitoVenta",

            "POSVenta",

            "POSHistorial",

            "POSCaja",

            "Remisiones",

            "FacturasCompra",

            "DocumentosSoporte",

            "RecibosCaja",

            "ComprobantesEgreso",

        ],

        "dias_predeterminados": 365,

    },

    "empresarial": {

        "codigo_serial": "EM",

        "nombre": "Empresarial",

        "modulos": ["*"],

        "max_usuarios": 999,

        "dias_predeterminados": None,

    },

}

CODIGO_A_EDICION = {

    datos["codigo_serial"]: codigo

    for codigo, datos in EDICIONES.items()

}
