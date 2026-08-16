from __future__ import annotations

from datetime import date

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.maestros.terceros.modelos import Tercero
from aplicacion.modulos.compras.facturas.modelos import FacturaCompra
from aplicacion.modulos.ventas.facturas.modelos import FacturaVenta


def _fila_vacia(
    tipo_documento: str,
    numero_documento: str,
    dv: str | None,
    nombre: str,
) -> dict:

    return {
        "tipo_documento": tipo_documento or "",
        "numero_documento": numero_documento or "",
        "dv": dv or "",
        "nombre": nombre or "",
        "valor_base": 0.0,
        "valor_iva": 0.0,
        "valor_retefuente": 0.0,
        "valor_reteica": 0.0,
        "valor_reteiva": 0.0,
        "valor_total": 0.0,
    }


def _acumular(
    fila: dict,
    documento,
) -> None:

    fila["valor_base"] += float(documento.subtotal or 0)
    fila["valor_iva"] += float(documento.iva or 0)
    fila["valor_retefuente"] += float(documento.valor_retefuente or 0)
    fila["valor_reteica"] += float(documento.valor_reteica or 0)
    fila["valor_reteiva"] += float(documento.valor_reteiva or 0)
    fila["valor_total"] += float(documento.total or 0)


class ServicioInformacionExogena:
    """
    Agrega, por tercero y para un año fiscal, los valores que un contador
    necesita para diligenciar el reporte anual de información exógena
    ante la DIAN (formatos 1001, 1003 y 1007) usando el prevalidador
    tributario oficial. No genera el archivo plano de envío: entrega los
    totales agrupados por tercero para que el contador los traslade.
    """

    @classmethod
    def pagos_y_retenciones(
        cls,
        anio: int,
    ) -> list[dict]:

        db = SessionLocal()

        try:

            facturas = (
                db.query(FacturaCompra)
                .filter(
                    FacturaCompra.activo.is_(True),
                    FacturaCompra.contabilizado.is_(True),
                    FacturaCompra.fecha >= date(anio, 1, 1),
                    FacturaCompra.fecha <= date(anio, 12, 31),
                )
                .all()
            )

            proveedor_ids = {
                factura.proveedor_id
                for factura in facturas
                if factura.proveedor_id
            }

            proveedores = {
                tercero.id: tercero
                for tercero in (
                    db.query(Tercero)
                    .filter(Tercero.id.in_(proveedor_ids))
                    .all()
                    if proveedor_ids
                    else []
                )
            }

            agrupado: dict[str, dict] = {}

            for factura in facturas:

                proveedor = proveedores.get(factura.proveedor_id)

                if proveedor is not None:

                    clave = f"tercero-{proveedor.id}"

                    fila = agrupado.setdefault(
                        clave,
                        _fila_vacia(
                            proveedor.tipo_documento,
                            proveedor.numero_documento,
                            proveedor.dv,
                            proveedor.nombre_completo,
                        ),
                    )

                else:

                    numero_documento = (
                        factura.nit_proveedor
                        or "SIN NIT"
                    )

                    clave = f"nit-{numero_documento}"

                    fila = agrupado.setdefault(
                        clave,
                        _fila_vacia(
                            "NIT",
                            numero_documento,
                            "",
                            factura.razon_social_proveedor
                            or numero_documento,
                        ),
                    )

                _acumular(fila, factura)

            return sorted(
                agrupado.values(),
                key=lambda fila: fila["nombre"],
            )

        finally:

            db.close()

    @classmethod
    def retenciones_que_le_practicaron(
        cls,
        anio: int,
    ) -> list[dict]:

        return cls._agrupar_ventas(
            anio,
            solo_con_retenciones=True,
        )

    @classmethod
    def ingresos_recibidos(
        cls,
        anio: int,
    ) -> list[dict]:

        return cls._agrupar_ventas(
            anio,
            solo_con_retenciones=False,
        )

    @classmethod
    def _agrupar_ventas(
        cls,
        anio: int,
        *,
        solo_con_retenciones: bool,
    ) -> list[dict]:

        db = SessionLocal()

        try:

            facturas = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.activo.is_(True),
                    FacturaVenta.contabilizado.is_(True),
                    FacturaVenta.fecha >= date(anio, 1, 1),
                    FacturaVenta.fecha <= date(anio, 12, 31),
                )
                .all()
            )

            cliente_ids = {
                factura.cliente_id
                for factura in facturas
            }

            clientes = {
                tercero.id: tercero
                for tercero in (
                    db.query(Tercero)
                    .filter(Tercero.id.in_(cliente_ids))
                    .all()
                    if cliente_ids
                    else []
                )
            }

            agrupado: dict[int, dict] = {}

            for factura in facturas:

                if solo_con_retenciones and not (
                    factura.valor_retefuente
                    or factura.valor_reteica
                    or factura.valor_reteiva
                ):

                    continue

                cliente = clientes.get(factura.cliente_id)

                if cliente is None:

                    continue

                fila = agrupado.setdefault(
                    cliente.id,
                    _fila_vacia(
                        cliente.tipo_documento,
                        cliente.numero_documento,
                        cliente.dv,
                        cliente.nombre_completo,
                    ),
                )

                _acumular(fila, factura)

            return sorted(
                agrupado.values(),
                key=lambda fila: fila["nombre"],
            )

        finally:

            db.close()
