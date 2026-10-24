"""
Color de acento por módulo (idea tomada de Sysplus: cada área del
negocio tiene su color, así uno sabe de un vistazo dónde está).

Los tonos son apagados para que combinen con el gris acero del tema.
"""

from __future__ import annotations

COLOR_POR_DEFECTO = "#1E3A5F"

# Clave: nombre del ícono del menú (ver GRUPOS en menu_manifest).
COLORES_AREA: dict[str, str] = {
    "inicio": "#1E3A5F",
    "ventas": "#2F6DB0",
    "pos": "#2F6DB0",
    "compras": "#C0661E",
    "logistica": "#6E58A8",
    "crm": "#23848A",
    "terceros": "#2E7D5B",
    "productos": "#A9801A",
    "bancos": "#2E8B57",
    "cartera": "#C9702A",
    "contabilidad": "#3B5998",
    "inventarios": "#A9801A",
    "nomina": "#86509C",
    "reportes": "#556677",
    "administracion": "#5E6875",
}

NOMBRE_AREA: dict[str, str] = {
    "inicio": "Inicio",
    "ventas": "Ventas",
    "pos": "Punto de venta",
    "compras": "Compras",
    "logistica": "Logística",
    "crm": "CRM",
    "terceros": "Terceros",
    "productos": "Productos",
    "bancos": "Tesorería",
    "cartera": "Cartera",
    "contabilidad": "Contabilidad",
    "inventarios": "Inventarios",
    "nomina": "Nómina",
    "reportes": "Reportes",
    "administracion": "Administración",
}

_cache: dict[str, str] | None = None


def _mapa_modulos() -> dict[str, str]:
    """modulo_id -> nombre del ícono del área a la que pertenece."""

    global _cache

    if _cache is not None:

        return _cache

    from aplicacion.framework.menu_manifest import GRUPOS

    mapa: dict[str, str] = {}

    for _titulo, entradas in GRUPOS:

        for entrada in entradas:

            icono = entrada.get(
                "icono",
                "",
            )

            if entrada.get(
                "modulo",
            ):

                mapa[
                    entrada["modulo"]
                ] = icono

            for _texto, modulo_id in entrada.get(
                "submenu",
                [],
            ) or []:

                mapa[
                    modulo_id
                ] = icono

    # Módulos que se abren desde un hub y no están en el menú.
    extras = {
        "compras": (
            "FacturasCompra",
            "DocumentosSoporte",
            "OrdenesCompra",
            "NotasCreditoCompra",
            "RecepcionesCompra",
            "ConfiguracionAprobacionCompras",
        ),
        "contabilidad": (
            "PlanCuentas",
            "ComprobantesContables",
            "LibroMayor",
            "ReglasContabilizacion",
            "BalancePrueba",
            "EstadoResultados",
        ),
        "inventarios": (
            "Bodegas",
            "Kardex",
            "AjustesInventario",
            "TrasladosInventario",
        ),
        "reportes": (
            "PanelGerencial",
            "InformacionExogena",
        ),
        "terceros": (
            "Terceros",
        ),
        "administracion": (
            "Empresas",
            "ModulosFuturos",
        ),
    }

    for icono, modulos in extras.items():

        for modulo_id in modulos:

            mapa.setdefault(
                modulo_id,
                icono,
            )

    _cache = mapa

    return mapa


_PREFIJOS = (
    ("Cartera", "cartera"),
    ("Nomina", "nomina"),
    ("CRM", "crm"),
    ("Reporte", "reportes"),
    ("POS", "pos"),
)


def _area_por_prefijo(
    modulo_id: str,
) -> str:

    for prefijo, icono in _PREFIJOS:

        if modulo_id.startswith(
            prefijo,
        ):

            return icono

    return ""


def area_modulo(
    modulo_id: str,
) -> str:

    return _mapa_modulos().get(
        modulo_id,
        "",
    ) or _area_por_prefijo(
        modulo_id,
    )


def color_modulo(
    modulo_id: str,
) -> str:

    return COLORES_AREA.get(
        area_modulo(
            modulo_id,
        ),
        COLOR_POR_DEFECTO,
    )


def nombre_area(
    modulo_id: str,
) -> str:

    return NOMBRE_AREA.get(
        area_modulo(
            modulo_id,
        ),
        "",
    )
