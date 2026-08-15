from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import func

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.productos.repositorio import (
    RepositorioProducto,
)
from aplicacion.maestros.terceros.repositorio import (
    TerceroRepositorio,
)
from aplicacion.modulos.ventas.cotizaciones.modelos import (
    Cotizacion,
)
from aplicacion.nucleo.configuracion import Configuracion


@dataclass(frozen=True)
class CotizacionReciente:

    id: int
    numero: str
    fecha: date
    total: float


@dataclass(frozen=True)
class ResumenInicio:

    empresa_nombre: str
    cotizaciones_hoy_cantidad: int
    cotizaciones_hoy_total: float
    cotizaciones_mes_cantidad: int
    cotizaciones_mes_total: float
    clientes_activos: int
    productos_activos: int
    cxc_total: float
    cxp_total: float
    cxc_vencido: float
    recientes: list[CotizacionReciente]


def _nombre_empresa() -> str:

    nombre = (
        Configuracion.obtener(
            "empresa",
            "nombre",
        )
        or ""
    ).strip()

    if nombre:

        return nombre

    from aplicacion.maestros.empresas.repositorio import (
        EmpresaRepositorio,
    )

    empresas = EmpresaRepositorio.obtener_todos(
        ordenar_por=(
            EmpresaRepositorio.modelo.id,
        ),
    )

    if not empresas:

        return ""

    activas = [
        empresa
        for empresa in empresas
        if empresa.activo
    ]

    empresa = (
        activas[0]
        if activas
        else empresas[0]
    )

    return (
        empresa.nombre_comercial
        or empresa.razon_social
        or ""
    ).strip()


def _contar_terceros_activos(
    tipo_tercero: str,
) -> int:

    db = TerceroRepositorio.obtener_sesion()

    try:

        return (
            db.query(
                TerceroRepositorio.modelo,
            )
            .filter(
                TerceroRepositorio.modelo.tipo_tercero
                == tipo_tercero,
                TerceroRepositorio.modelo.activo.is_(
                    True,
                ),
            )
            .count()
        )

    finally:

        db.close()


def _contar_productos_activos() -> int:

    db = RepositorioProducto.obtener_sesion()

    try:

        return (
            db.query(
                RepositorioProducto.modelo,
            )
            .filter(
                RepositorioProducto.modelo.activo.is_(
                    True,
                ),
            )
            .count()
        )

    finally:

        db.close()


def obtener_resumen_inicio() -> ResumenInicio:

    hoy = date.today()
    inicio_mes = hoy.replace(
        day=1,
    )

    db = SessionLocal()

    try:

        filtro_hoy = (
            db.query(
                func.count(
                    Cotizacion.id,
                ),
                func.coalesce(
                    func.sum(
                        Cotizacion.total,
                    ),
                    0.0,
                ),
            )
            .filter(
                Cotizacion.fecha == hoy,
            )
            .one()
        )

        filtro_mes = (
            db.query(
                func.count(
                    Cotizacion.id,
                ),
                func.coalesce(
                    func.sum(
                        Cotizacion.total,
                    ),
                    0.0,
                ),
            )
            .filter(
                Cotizacion.fecha
                >= inicio_mes,
                Cotizacion.fecha
                <= hoy,
            )
            .one()
        )

        recientes = (
            db.query(
                Cotizacion,
            )
            .order_by(
                Cotizacion.fecha.desc(),
                Cotizacion.numero.desc(),
            )
            .limit(
                5,
            )
            .all()
        )

    finally:

        db.close()

    from aplicacion.modulos.cartera.servicios import (
        ServicioCartera,
    )

    cartera = ServicioCartera.resumen()

    return ResumenInicio(
        empresa_nombre=_nombre_empresa(),
        cotizaciones_hoy_cantidad=int(
            filtro_hoy[0]
            or 0,
        ),
        cotizaciones_hoy_total=float(
            filtro_hoy[1]
            or 0,
        ),
        cotizaciones_mes_cantidad=int(
            filtro_mes[0]
            or 0,
        ),
        cotizaciones_mes_total=float(
            filtro_mes[1]
            or 0,
        ),
        clientes_activos=_contar_terceros_activos(
            "Cliente",
        ),
        productos_activos=_contar_productos_activos(),
        cxc_total=float(
            cartera["cxc_total"],
        ),
        cxp_total=float(
            cartera["cxp_total"],
        ),
        cxc_vencido=float(
            cartera["cxc_vencido"],
        ),
        recientes=[
            CotizacionReciente(
                id=item.id,
                numero=item.numero,
                fecha=item.fecha,
                total=float(
                    item.total
                    or 0,
                ),
            )
            for item in recientes
        ],
    )


def formatear_moneda(
    valor: float,
) -> str:

    return (
        f"$ {valor:,.0f}".replace(
            ",",
            ".",
        )
    )
