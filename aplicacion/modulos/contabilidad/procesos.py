from __future__ import annotations

CUENTAS_CONTABLES: list[
    tuple[
        str,
        list[str],
    ]
] = [

    (
        "Maestros contables",
        [

            "Plan de cuentas",

            "Centros de costo",

            "Tipos de comprobante",

        ],
    ),

    (
        "Movimiento contable",
        [

            "Comprobantes contables",

            "Libro mayor",

            "Balance de prueba",

            "Estado de resultados",

        ],
    ),

    (
        "Configuración",
        [

            "Empresas",

            "Parámetros contables",

        ],
    ),

]

MAS_PROCESOS: list[
    tuple[
        str,
        list[str],
    ]
] = [

    (
        "Contables",
        [

            "Diferencia en cambio",

            "Cierre de año",

            "Cierre cuentas de impuestos y otras cuentas por tercero",

            "Verifica y bloquea documentos",

            "Copias de comprobantes favoritos",

            "Borrado masivo de comprobantes",

        ],
    ),

    (
        "Medios Magnéticos",
        [

            "Asistente de medios magnéticos",

            "Informe auxiliar medios magnéticos distritales y/o municipales",

        ],
    ),

    (
        "Activos fijos",
        [

            "Creación de activo fijo",

            "Importar activo fijo",

        ],
    ),

    (
        "Certificados",
        [

            "Generar certificado de retención a título de renta, IVA e ICA",

            "Generar certificado de ingresos y retenciones / Formulario 220",

        ],
    ),

    (
        "Saldos Iniciales",
        [

            "Saldos iniciales de cuentas por cobrar",

            "Saldos iniciales de cuentas por pagar",

            "Saldos iniciales de inventario",

        ],
    ),

    (
        "Saldos iniciales otras cuentas",
        [

            "Saldos iniciales de otras cuentas contables",

        ],
    ),

]

MODULOS_ENLACE: dict[
    str,
    str,
] = {

    "Plan de cuentas": "PlanCuentas",

    "Comprobantes contables": "ComprobantesContables",

    "Libro mayor": "LibroMayor",

    "Balance de prueba": "BalancePrueba",

    "Estado de resultados": "EstadoResultados",

    "Empresas": "Empresas",

}
