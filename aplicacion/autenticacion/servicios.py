from __future__ import annotations

from aplicacion.autenticacion.modelos import Rol, Usuario
from aplicacion.autenticacion.seguridad import (
    cifrar_password,
    verificar_password,
)
from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.nucleo.permisos import Permisos


ROLES_PREDETERMINADOS: dict[
    str,
    dict,
] = {

    "admin": {

        "nombre": "Administrador",

        "modulos": ["*"],

    },

    "vendedor": {

        "nombre": "Vendedor",

        "modulos": [

            "Cotizaciones",

            "Pedidos",

            "FacturasVenta",

            "NotasCreditoVenta",

            "NotasDebitoVenta",

            "POSVenta",

            "POSHistorial",

            "POSCaja",

            "Remisiones",

            "GuiasRemisionElectronica",

            "RecibosCaja",

            "Clientes",

            "Productos",

            "Categorías",

            "Marcas",

        ],

    },

    "compras": {

        "nombre": "Compras",

        "modulos": [

            "FacturasCompra",

            "NotasCreditoCompra",

            "DocumentosSoporte",

            "Compras",

            "OrdenesCompra",

            "RecepcionesCompra",

            "ComprobantesEgreso",

            "Proveedores",

            "Productos",

            "Categorías",

            "Marcas",

            "Reportes",

            "ReporteCompras",

            "ReporteInventario",

        ],

    },

    "contabilidad": {

        "nombre": "Contabilidad",

        "modulos": [

            "Contabilidad",

            "PlanCuentas",

            "ComprobantesContables",

            "LibroMayor",

            "BalancePrueba",

            "Inventarios",

            "Bodegas",

            "Kardex",

            "AjustesInventario",

            "TrasladosInventario",

            "Cartera",

            "CarteraCxC",

            "CarteraCxP",

            "CarteraAntiguedad",

            "CarteraEstadoCuenta",

            "Reportes",

            "ReporteVentas",

            "ReporteCompras",

            "ReporteInventario",

            "ReporteCartera",

            "ReporteRetenciones",

            "InformacionExogena",

            "Compras",

            "OrdenesCompra",

            "RecepcionesCompra",

            "Empresas",

            "FacturasCompra",

            "NotasCreditoCompra",

            "DocumentosSoporte",

            "FacturasVenta",

            "NotasCreditoVenta",

            "NotasDebitoVenta",

            "RecibosCaja",

            "ComprobantesEgreso",

        ],

    },

}


def inicializar_roles() -> None:

    db = SessionLocal()

    try:

        for (
            codigo,
            datos,
        ) in ROLES_PREDETERMINADOS.items():

            rol = (
                db.query(Rol)
                .filter(
                    Rol.codigo == codigo,
                )
                .first()
            )

            if rol is None:

                db.add(
                    Rol(
                        codigo=codigo,
                        nombre=datos[
                            "nombre"
                        ],
                        modulos=datos[
                            "modulos"
                        ],
                        activo=True,
                    ),
                )

                continue

            rol.nombre = datos[
                "nombre"
            ]

            if not rol.modulos:

                rol.modulos = datos[
                    "modulos"
                ]

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


def crear_usuario_admin() -> None:

    db = SessionLocal()

    try:

        inicializar_roles()

        rol_admin = (
            db.query(Rol)
            .filter(
                Rol.codigo == "admin",
            )
            .first()
        )

        usuario = (
            db.query(Usuario)
            .filter(
                Usuario.usuario == "admin",
            )
            .first()
        )

        if usuario is None:

            admin = Usuario(
                usuario="admin",
                nombre="Administrador",
                correo="admin@erpnexus.com",
                password=cifrar_password(
                    "Admin123",
                ),
                rol_id=(
                    rol_admin.id
                    if rol_admin
                    else None
                ),
                activo=True,
            )

            db.add(
                admin,
            )

            db.commit()

            return

        if (
            rol_admin is not None
            and usuario.rol_id is None
        ):

            usuario.rol_id = rol_admin.id

            db.commit()

    finally:

        db.close()


def autenticar(
    usuario: str,
    password: str,
):

    db = SessionLocal()

    try:

        registro = (
            db.query(Usuario)
            .filter(
                Usuario.usuario == usuario,
            )
            .first()
        )

        if registro is None:

            return None

        if not registro.activo:

            return None

        if not verificar_password(
            password,
            registro.password,
        ):

            return None

        if registro.rol_id:

            rol = (
                db.query(Rol)
                .filter(
                    Rol.id
                    == registro.rol_id,
                )
                .first()
            )

            if rol is not None:

                registro.rol = rol

        return registro

    finally:

        db.close()


def cargar_permisos_usuario(
    usuario,
) -> None:

    modulos: list | None = ["*"]

    rol_codigo = "admin"

    rol = getattr(
        usuario,
        "rol",
        None,
    )

    if rol is not None:

        modulos = list(
            rol.modulos or [],
        )

        rol_codigo = str(
            rol.codigo or "",
        )

    elif getattr(
        usuario,
        "rol_id",
        None,
    ):

        db = SessionLocal()

        try:

            rol = (
                db.query(Rol)
                .filter(
                    Rol.id
                    == usuario.rol_id,
                )
                .first()
            )

            if rol is not None:

                modulos = list(
                    rol.modulos or [],
                )

                rol_codigo = str(
                    rol.codigo or "",
                )

        finally:

            db.close()

    Permisos.cargar_modulos(
        modulos,
        rol_codigo=rol_codigo,
    )
