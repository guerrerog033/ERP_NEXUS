from __future__ import annotations

import tempfile
from pathlib import Path


class ServicioPortalTercero:
    """
    Datos y documentos expuestos al portal de autoconsulta de
    clientes/proveedores (``/portal/mi-cuenta/<token>``).

    Todo acceso pasa primero por resolver el ``portal_token`` a un
    Tercero — un token inválido o vacío nunca revela datos de
    ningún tercero (ver ``_tercero_o_none``).
    """

    @classmethod
    def _tercero_o_none(
        cls,
        token: str,
    ):

        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )

        if not token:

            return None

        return TerceroServicio.obtener_por_token_portal(
            token,
        )

    @classmethod
    def datos_cuenta(
        cls,
        token: str,
    ) -> dict | None:

        tercero = cls._tercero_o_none(
            token,
        )

        if tercero is None or not tercero.activo:

            return None

        facturas_venta: list[dict] = []
        facturas_compra: list[dict] = []

        if tercero.es_cliente:

            facturas_venta = cls._facturas_venta(
                tercero.id,
            )

        if tercero.es_proveedor:

            facturas_compra = cls._facturas_compra(
                tercero.id,
            )

        return {
            "nombre": tercero.nombre_completo,
            "documento": tercero.numero_documento,
            "facturas_venta": facturas_venta,
            "facturas_compra": facturas_compra,
        }

    @classmethod
    def _facturas_venta(
        cls,
        cliente_id: int,
    ) -> list[dict]:

        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        db = SessionLocal()

        try:

            facturas = (
                db.query(
                    FacturaVenta,
                )
                .filter(
                    FacturaVenta.cliente_id
                    == cliente_id,
                    FacturaVenta.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    FacturaVenta.fecha.desc(),
                )
                .all()
            )

            return [
                {
                    "id": factura.id,
                    "numero": factura.numero,
                    "fecha": str(
                        factura.fecha or "",
                    ),
                    "total": float(
                        factura.total or 0,
                    ),
                    "saldo_pendiente": float(
                        factura.saldo_pendiente or 0,
                    ),
                    "estado_pago": factura.estado_pago,
                    "tiene_xml": bool(
                        factura.ruta_xml,
                    ),
                }
                for factura in facturas
            ]

        finally:

            db.close()

    @classmethod
    def _facturas_compra(
        cls,
        proveedor_id: int,
    ) -> list[dict]:

        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )
        from aplicacion.modulos.compras.facturas.modelos import (
            FacturaCompra,
        )

        db = SessionLocal()

        try:

            facturas = (
                db.query(
                    FacturaCompra,
                )
                .filter(
                    FacturaCompra.proveedor_id
                    == proveedor_id,
                    FacturaCompra.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    FacturaCompra.fecha.desc(),
                )
                .all()
            )

            return [
                {
                    "id": factura.id,
                    "numero": factura.numero,
                    "fecha": str(
                        factura.fecha or "",
                    ),
                    "total": float(
                        factura.total or 0,
                    ),
                    "saldo_pendiente": float(
                        factura.saldo_pendiente or 0,
                    ),
                    "estado_pago": factura.estado_pago,
                    "tiene_xml": bool(
                        factura.ruta_xml,
                    ),
                }
                for factura in facturas
            ]

        finally:

            db.close()

    @classmethod
    def pdf_factura_venta(
        cls,
        token: str,
        factura_id: int,
    ) -> Path | None:

        tercero = cls._tercero_o_none(
            token,
        )

        if tercero is None or not tercero.es_cliente:

            return None

        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )
        from aplicacion.reportes.ventas.factura import (
            ReporteFacturaVenta,
        )

        factura = ServicioFacturaVenta.obtener_completa(
            factura_id,
        )

        if (
            factura is None
            or factura.cliente_id != tercero.id
        ):

            return None

        destino = (
            Path(
                tempfile.gettempdir(),
            )
            / f"portal_factura_venta_{factura.id}.pdf"
        )

        reporte = ReporteFacturaVenta(
            factura,
            list(
                factura.detalles or [],
            ),
            tercero.nombre_completo,
        )

        return reporte.construir_pdf_reportlab(
            destino,
        )

    @classmethod
    def xml_factura_venta(
        cls,
        token: str,
        factura_id: int,
    ) -> Path | None:

        tercero = cls._tercero_o_none(
            token,
        )

        if tercero is None or not tercero.es_cliente:

            return None

        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        factura = ServicioFacturaVenta.obtener_completa(
            factura_id,
        )

        if (
            factura is None
            or factura.cliente_id != tercero.id
            or not factura.ruta_xml
        ):

            return None

        ruta = Path(
            factura.ruta_xml,
        )

        return (
            ruta
            if ruta.is_file()
            else None
        )

    @classmethod
    def pdf_factura_compra(
        cls,
        token: str,
        factura_id: int,
    ) -> Path | None:

        tercero = cls._tercero_o_none(
            token,
        )

        if tercero is None or not tercero.es_proveedor:

            return None

        from aplicacion.modulos.compras.facturas.servicios import (
            ServicioFacturaCompra,
        )
        from aplicacion.reportes.compras.factura import (
            _construir_pdf_factura_compra,
        )

        factura = ServicioFacturaCompra.obtener_completa(
            factura_id,
        )

        if (
            factura is None
            or factura.proveedor_id != tercero.id
        ):

            return None

        destino = (
            Path(
                tempfile.gettempdir(),
            )
            / f"portal_factura_compra_{factura.id}.pdf"
        )

        return _construir_pdf_factura_compra(
            factura,
            list(
                factura.detalles or [],
            ),
            tercero.nombre_completo,
            destino,
            documento_proveedor=str(
                tercero.numero_documento or "",
            ),
            correo_proveedor=str(
                tercero.correo or "",
            ),
        )

    @classmethod
    def xml_factura_compra(
        cls,
        token: str,
        factura_id: int,
    ) -> Path | None:

        tercero = cls._tercero_o_none(
            token,
        )

        if tercero is None or not tercero.es_proveedor:

            return None

        from aplicacion.modulos.compras.facturas.servicios import (
            ServicioFacturaCompra,
        )

        factura = ServicioFacturaCompra.obtener_completa(
            factura_id,
        )

        if (
            factura is None
            or factura.proveedor_id != tercero.id
            or not factura.ruta_xml
        ):

            return None

        ruta = Path(
            factura.ruta_xml,
        )

        return (
            ruta
            if ruta.is_file()
            else None
        )
