from __future__ import annotations

from dataclasses import dataclass

from aplicacion.maestros.empresas.maestro import MaestroEmpresas
from aplicacion.integraciones.dian.configuracion_pagina import (
    ConfiguracionDianPage,
)
from aplicacion.maestros.categorias.maestro import MaestroCategorias
from aplicacion.maestros.marcas.maestro import MaestroMarcas
from aplicacion.maestros.productos.maestro import MaestroProductos
from aplicacion.maestros.productos.maestro_variantes import MaestroCatalogoVariantes
from aplicacion.maestros.impuestos.maestro import MaestroImpuestos
from aplicacion.maestros.listas_precio.maestro import MaestroListasPrecio
from aplicacion.maestros.terceros.maestro import (
    MaestroClientes,
    MaestroOtros,
    MaestroProveedores,
    MaestroTerceros,
)
from aplicacion.modulos.ventas.cotizaciones.maestro import (
    MaestroCotizaciones,
)
from aplicacion.modulos.ventas.pedidos.maestro import (
    MaestroPedidos,
)
from aplicacion.modulos.ventas.facturas.maestro import (
    MaestroFacturasVenta,
)
from aplicacion.modulos.ventas.notas_credito.maestro import (
    MaestroNotasCreditoVenta,
)
from aplicacion.modulos.ventas.notas_debito.maestro import (
    MaestroNotasDebitoVenta,
)
from aplicacion.modulos.ventas.pos.vista import (
    POSVentaPage,
)
from aplicacion.modulos.ventas.pos.historial import (
    POSHistorialPage,
)
from aplicacion.modulos.ventas.pos.dashboard import (
    POSCajaPage,
)
from aplicacion.modulos.compras.documentos_soporte.maestro import (
    MaestroDocumentosSoporte,
)
from aplicacion.modulos.ventas.remisiones.maestro import (
    MaestroRemisiones,
)
from aplicacion.modulos.ventas.guias_remision.maestro import (
    MaestroGuiasRemisionElectronica,
)
from aplicacion.modulos.logistica.despacho.vista import (
    DespachosLogisticaPage,
)
from aplicacion.modulos.compras.facturas.maestro import (
    MaestroFacturasCompra,
)
from aplicacion.modulos.compras.notas_credito.maestro import (
    MaestroNotasCreditoCompra,
)
from aplicacion.modulos.tesoreria.recibos_caja.maestro import (
    MaestroRecibosCaja,
)
from aplicacion.modulos.tesoreria.comprobantes_egreso.maestro import (
    MaestroComprobantesEgreso,
)
from aplicacion.modulos.tesoreria.conciliacion.vista import (
    ConciliacionBancariaPage,
)
from aplicacion.modulos.contabilidad.hub import (
    HubContabilidad,
)
from aplicacion.modulos.contabilidad.comprobantes.maestro import (
    MaestroComprobantes,
)
from aplicacion.modulos.contabilidad.plan_cuentas.maestro import (
    MaestroPlanCuentas,
)
from aplicacion.modulos.contabilidad.reportes.balance_prueba import (
    BalancePruebaPage,
)
from aplicacion.modulos.contabilidad.reportes.estado_resultados import (
    EstadoResultadosPage,
)
from aplicacion.modulos.contabilidad.reportes.libro_mayor import (
    LibroMayorPage,
)
from aplicacion.modulos.contabilidad.reglas.vista import (
    ReglasContabilizacionPage,
)
from aplicacion.modulos.inventario.hub import (
    HubInventarios,
)
from aplicacion.modulos.inventario.bodegas.maestro import (
    MaestroBodegas,
)
from aplicacion.modulos.inventario.kardex.vista import (
    KardexPage,
)
from aplicacion.modulos.inventario.ajustes.vista import (
    AjustesInventarioPage,
)
from aplicacion.modulos.inventario.traslados.vista import (
    TrasladosInventarioPage,
)
from aplicacion.modulos.futuro.hub import (
    HubModulosFuturos,
)
from aplicacion.modulos.cartera.hub import (
    HubCartera,
)
from aplicacion.modulos.cartera.cxc.vista import (
    CarteraCxCPage,
)
from aplicacion.modulos.cartera.cxp.vista import (
    CarteraCxPPage,
)
from aplicacion.modulos.cartera.antiguedad.vista import (
    CarteraAntiguedadPage,
)
from aplicacion.modulos.cartera.estado_cuenta.vista import (
    CarteraEstadoCuentaPage,
)
from aplicacion.modulos.cartera.configuracion_pagina import (
    ConfiguracionCarteraPage,
)
from aplicacion.modulos.reportes.hub import (
    HubReportes,
)
from aplicacion.modulos.reportes.comercial.vista import (
    ReportePipelineComercialPage,
)
from aplicacion.modulos.gerencial.vista import (
    PanelGerencialPage,
)
from aplicacion.modulos.reportes.ventas.vista import (
    ReporteVentasPage,
)
from aplicacion.modulos.reportes.compras.vista import (
    ReporteComprasPage,
)
from aplicacion.modulos.reportes.inventario.vista import (
    ReporteInventarioPage,
)
from aplicacion.modulos.reportes.cartera.vista import (
    ReporteCarteraPage,
)
from aplicacion.modulos.reportes.impuestos.vista import (
    ReporteRetencionesPage,
)
from aplicacion.modulos.reportes.exogena.vista import (
    InformacionExogenaPage,
)
from aplicacion.modulos.compras.hub import (
    HubCompras,
)
from aplicacion.modulos.compras.ordenes.vista import (
    OrdenesCompraPage,
)
from aplicacion.modulos.compras.recepciones.vista import (
    RecepcionesCompraPage,
)
from aplicacion.modulos.nomina.hub import (
    HubNomina,
)
from aplicacion.modulos.nomina.empleados.maestro import (
    MaestroEmpleados,
)
from aplicacion.modulos.nomina.liquidacion.vista import (
    LiquidacionNominaPage,
)
from aplicacion.modulos.nomina.contratos.maestro import (
    MaestroContratos,
)
from aplicacion.modulos.nomina.novedades.maestro import (
    MaestroNovedades,
)
from aplicacion.modulos.nomina.prestaciones.vista import (
    PrestacionesNominaPage,
)
from aplicacion.modulos.crm.hub import (
    HubCRM,
)
from aplicacion.modulos.crm.oportunidades.maestro import (
    MaestroOportunidades,
)
from aplicacion.modulos.crm.actividades.maestro import (
    MaestroActividadesCRM,
)
from aplicacion.modulos.reportes.nomina.vista import (
    ReporteNominaPage,
)
from aplicacion.seguridad.usuarios.maestro import (
    MaestroUsuarios,
)
from aplicacion.seguridad.roles.maestro import (
    MaestroRoles,
)
from aplicacion.seguridad.auditoria.vista import (
    VistaAuditoria,
)


from aplicacion.framework.menu_ids import (
    MODULO_INICIO,
    MODULO_PENDIENTE,
)


MODULOS = {

    "Empresas": MaestroEmpresas,

    "ConfiguracionDian": ConfiguracionDianPage,

    "Categorías": MaestroCategorias,

    "Marcas": MaestroMarcas,

    "Productos": MaestroProductos,

    "Variantes": MaestroCatalogoVariantes,

    "Impuestos": MaestroImpuestos,

    "ListasPrecio": MaestroListasPrecio,

    "Terceros": MaestroTerceros,

    "Clientes": MaestroClientes,

    "Proveedores": MaestroProveedores,

    "Otros": MaestroOtros,

    "Cotizaciones": MaestroCotizaciones,

    "Pedidos": MaestroPedidos,

    "FacturasVenta": MaestroFacturasVenta,

    "NotasCreditoVenta": MaestroNotasCreditoVenta,

    "NotasDebitoVenta": MaestroNotasDebitoVenta,

    "POSVenta": POSVentaPage,

    "POSHistorial": POSHistorialPage,

    "POSCaja": POSCajaPage,

    "Remisiones": MaestroRemisiones,

    "GuiasRemisionElectronica": MaestroGuiasRemisionElectronica,

    "DespachosLogistica": DespachosLogisticaPage,

    "FacturasCompra": MaestroFacturasCompra,

    "NotasCreditoCompra": MaestroNotasCreditoCompra,

    "DocumentosSoporte": MaestroDocumentosSoporte,

    "RecibosCaja": MaestroRecibosCaja,

    "ComprobantesEgreso": MaestroComprobantesEgreso,

    "ConciliacionBancaria": ConciliacionBancariaPage,

    "Contabilidad": HubContabilidad,

    "PlanCuentas": MaestroPlanCuentas,

    "ComprobantesContables": MaestroComprobantes,

    "LibroMayor": LibroMayorPage,

    "ReglasContabilizacion": ReglasContabilizacionPage,

    "BalancePrueba": BalancePruebaPage,

    "EstadoResultados": EstadoResultadosPage,

    "Inventarios": HubInventarios,

    "Bodegas": MaestroBodegas,

    "Kardex": KardexPage,

    "AjustesInventario": AjustesInventarioPage,

    "TrasladosInventario": TrasladosInventarioPage,

    "Cartera": HubCartera,

    "CarteraCxC": CarteraCxCPage,

    "CarteraCxP": CarteraCxPPage,

    "CarteraAntiguedad": CarteraAntiguedadPage,

    "CarteraEstadoCuenta": CarteraEstadoCuentaPage,

    "ConfiguracionCartera": ConfiguracionCarteraPage,

    "Reportes": HubReportes,

    "ReportePipelineComercial": ReportePipelineComercialPage,

    "PanelGerencial": PanelGerencialPage,

    "ReporteVentas": ReporteVentasPage,

    "ReporteCompras": ReporteComprasPage,

    "ReporteInventario": ReporteInventarioPage,

    "ReporteCartera": ReporteCarteraPage,

    "ReporteRetenciones": ReporteRetencionesPage,

    "InformacionExogena": InformacionExogenaPage,

    "Compras": HubCompras,

    "OrdenesCompra": OrdenesCompraPage,

    "RecepcionesCompra": RecepcionesCompraPage,

    "Nomina": HubNomina,

    "NominaEmpleados": MaestroEmpleados,

    "NominaContratos": MaestroContratos,

    "NominaNovedades": MaestroNovedades,

    "NominaLiquidacion": LiquidacionNominaPage,

    "NominaPrestaciones": PrestacionesNominaPage,

    "CRM": HubCRM,

    "CRMOportunidades": MaestroOportunidades,

    "CRMActividades": MaestroActividadesCRM,

    "ReporteNomina": ReporteNominaPage,

    "ModulosFuturos": HubModulosFuturos,

    "AdminUsuarios": MaestroUsuarios,

    "AdminRoles": MaestroRoles,

    "AdminAuditoria": VistaAuditoria,

}


from aplicacion.licencias.admin.maestro import (
    MaestroAdminLicencias,
)

MODULOS[
    "AdminLicencias"
] = MaestroAdminLicencias


GRUPOS: list[
    tuple[
        str,
        list[dict],
    ]
] = [

    (
        "Operaciones",
        [

            {
                "icono": "inicio",
                "titulo": "Inicio",
                "modulo": MODULO_INICIO,
            },

            {
                "icono": "ventas",
                "titulo": "Ventas",
                "submenu": [

                    ("Cotizaciones", "Cotizaciones"),

                    ("Pedidos", "Pedidos"),

                    ("Facturas de venta", "FacturasVenta"),

                    ("Notas crédito", "NotasCreditoVenta"),

                    ("Notas débito", "NotasDebitoVenta"),

                    ("Punto de venta", "POSVenta"),

                    ("Historial POS", "POSHistorial"),

                    ("Caja POS", "POSCaja"),

                    ("Remisiones internas", "Remisiones"),

                    ("Guías remisión electrónica", "GuiasRemisionElectronica"),

                    ("Recibos de caja", "RecibosCaja"),

                ],
            },

            {
                "icono": "logistica",
                "titulo": "Logística",
                "submenu": [

                    ("Despachos", "DespachosLogistica"),

                ],
            },

            {
                "icono": "compras",
                "titulo": "Compras y gastos",
                "modulo": "Compras",
            },

        ],
    ),

    (
        "Maestros",
        [

            {
                "icono": "terceros",
                "titulo": "Terceros",
                "submenu": [

                    ("Clientes", "Clientes"),

                    ("Proveedores", "Proveedores"),

                    ("Otros", "Otros"),

                ],
            },

            {
                "icono": "productos",
                "titulo": "Productos y servicios",
                "submenu": [

                    ("Categorías", "Categorías"),

                    ("Marcas", "Marcas"),

                    ("Productos", "Productos"),

                    ("Variantes", "Variantes"),

                    ("Listas de precio", "ListasPrecio"),

                    ("Impuestos", "Impuestos"),

                ],
            },

        ],
    ),

    (
        "Financiero",
        [

            {
                "icono": "bancos",
                "titulo": "Cajas y bancos",
                "submenu": [

                    ("Recibos de caja", "RecibosCaja"),

                    ("Comprobantes de egreso", "ComprobantesEgreso"),

                    ("Conciliación bancaria", "ConciliacionBancaria"),

                ],
            },

            {
                "icono": "contabilidad",
                "titulo": "Contabilidad",
                "modulo": "Contabilidad",
            },

            {
                "icono": "productos",
                "titulo": "Inventarios",
                "modulo": "Inventarios",
            },

            {
                "icono": "bancos",
                "titulo": "Cartera",
                "modulo": "Cartera",
            },

            {
                "icono": "contabilidad",
                "titulo": "Reportes",
                "modulo": "Reportes",
            },

            {
                "icono": "nomina",
                "titulo": "Nómina",
                "modulo": "Nomina",
            },

            {
                "icono": "terceros",
                "titulo": "CRM",
                "modulo": "CRM",
            },

        ],
    ),

    (
        "Seguridad",
        [

            {
                "icono": "terceros",
                "titulo": "Accesos",
                "submenu": [

                    ("Usuarios", "AdminUsuarios"),

                    ("Roles", "AdminRoles"),

                    ("Auditoría", "AdminAuditoria"),

                ],
            },

        ],
    ),

    (
        "Administración",
        [

            {
                "icono": "contabilidad",
                "titulo": "Licencias",
                "modulo": "AdminLicencias",
            },

            {
                "icono": "contabilidad",
                "titulo": "Configuración DIAN",
                "modulo": "ConfiguracionDian",
            },

        ],
    ),

]


@dataclass(frozen=True)
class ResultadoBusqueda:

    modulo_id: str
    titulo: str
    grupo: str
    ruta: str
    pendiente: bool = False


def iter_enlaces() -> list[ResultadoBusqueda]:

    enlaces: list[ResultadoBusqueda] = []

    for grupo, entradas in grupos_visibles():

        for entrada in entradas:

            submenu = entrada.get(
                "submenu",
            )

            pendiente_entrada = bool(
                entrada.get(
                    "pendiente",
                ),
            )

            if submenu:

                for titulo, modulo_id in submenu:

                    enlaces.append(
                        ResultadoBusqueda(
                            modulo_id=modulo_id,
                            titulo=titulo,
                            grupo=grupo,
                            ruta=(
                                f"{entrada['titulo']} › {titulo}"
                            ),
                            pendiente=(
                                pendiente_entrada
                                or not modulo_accesible(
                                    modulo_id,
                                )
                            ),
                        ),
                    )

                continue

            modulo_id = entrada.get(
                "modulo",
                "",
            )

            if not modulo_id:

                continue

            enlaces.append(
                ResultadoBusqueda(
                    modulo_id=modulo_id,
                    titulo=entrada[
                        "titulo"
                    ],
                    grupo=grupo,
                    ruta=entrada[
                        "titulo"
                    ],
                    pendiente=(
                        pendiente_entrada
                        or modulo_id
                        == MODULO_PENDIENTE
                    ),
                ),
            )

    return enlaces


def modulo_disponible(
    modulo_id: str,
) -> bool:

    if modulo_id in (
        MODULO_INICIO,
        MODULO_PENDIENTE,
    ):

        return modulo_id == MODULO_INICIO

    return modulo_id in MODULOS


def modulo_accesible(
    modulo_id: str,
) -> bool:

    if not modulo_disponible(
        modulo_id,
    ):

        return modulo_id == MODULO_INICIO

    from aplicacion.nucleo.permisos import (
        Permisos,
    )

    return Permisos.puede_modulo(
        modulo_id,
    )


def _entrada_visible(
    entrada: dict,
) -> bool:

    from aplicacion.nucleo.permisos import (
        Permisos,
    )

    if entrada.get(
        "pendiente",
    ):

        return True

    submenu = entrada.get(
        "submenu",
    )

    if submenu:

        return any(
            Permisos.puede_modulo(
                modulo_id,
            )
            for _, modulo_id in submenu
        )

    modulo_id = entrada.get(
        "modulo",
        "",
    )

    return Permisos.puede_modulo(
        modulo_id,
    )


def _filtrar_submenu(
    submenu: list[
        tuple[
            str,
            str,
        ]
    ],
) -> list[
    tuple[
        str,
        str,
    ]
]:

    from aplicacion.nucleo.permisos import (
        Permisos,
    )

    return [
        (
            titulo,
            modulo_id,
        )
        for titulo, modulo_id in submenu
        if Permisos.puede_modulo(
            modulo_id,
        )
    ]


def grupos_visibles() -> list[
    tuple[
        str,
        list[dict],
    ]
]:

    grupos: list[
        tuple[
            str,
            list[dict],
        ]
    ] = []

    for titulo_grupo, entradas in GRUPOS:

        visibles: list[dict] = []

        for entrada in entradas:

            if not _entrada_visible(
                entrada,
            ):

                continue

            copia = dict(
                entrada,
            )

            submenu = copia.get(
                "submenu",
            )

            if submenu:

                copia[
                    "submenu"
                ] = _filtrar_submenu(
                    submenu,
                )

            visibles.append(
                copia,
            )

        if visibles:

            grupos.append(
                (
                    titulo_grupo,
                    visibles,
                ),
            )

    return grupos


def entradas_menu() -> list[dict]:

    items: list[dict] = []

    for _, entradas in grupos_visibles():

        items.extend(
            entradas,
        )

    return items


def es_pendiente(
    modulo_id: str,
) -> bool:

    if modulo_id == MODULO_PENDIENTE:

        return True

    for resultado in iter_enlaces():

        if (
            resultado.modulo_id
            == modulo_id
        ):

            return resultado.pendiente

    return False


def etiqueta_modulo(
    modulo_id: str,
) -> str:

    if modulo_id == MODULO_INICIO:

        return "Inicio"

    for resultado in iter_enlaces():

        if (
            resultado.modulo_id
            == modulo_id
        ):

            return resultado.titulo

    return modulo_id


def buscar_modulos(
    consulta: str,
    *,
    limite: int = 15,
) -> list[ResultadoBusqueda]:

    texto = consulta.strip().lower()

    enlaces = iter_enlaces()

    if not texto:

        return enlaces[
            :limite
        ]

    resultados: list[
        ResultadoBusqueda
    ] = []

    for enlace in enlaces:

        if not modulo_accesible(
            enlace.modulo_id,
        ) and enlace.modulo_id != MODULO_PENDIENTE:

            continue

        if (
            texto
            in enlace.titulo.lower()
            or texto
            in enlace.modulo_id.lower()
            or texto
            in enlace.grupo.lower()
            or texto
            in enlace.ruta.lower()
        ):

            resultados.append(
                enlace,
            )

    return resultados[
        :limite
    ]


def buscar_modulo(
    consulta: str,
) -> str | None:

    resultados = buscar_modulos(
        consulta,
        limite=1,
    )

    if not resultados:

        return None

    return resultados[
        0
    ].modulo_id
