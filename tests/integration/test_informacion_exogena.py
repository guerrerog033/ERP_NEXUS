from __future__ import annotations

import os
import uuid
from datetime import date

import pytest

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)

pytestmark = pytest.mark.integration


@pytest.fixture(
    scope="session",
    autouse=True,
)
def _registrar_modelos():

    importar_modelos()


@pytest.fixture(
    scope="session",
)
def requiere_postgresql():

    if not os.getenv(
        "DB_HOST",
    ):

        pytest.skip(
            "DB_HOST no configurado",
        )


def _sufijo() -> str:

    return uuid.uuid4().hex[:8]


def _documento(sufijo: str) -> str:

    return str(
        900000000
        + int(sufijo[:6], 16) % 99999999,
    )


def _crear_tercero(tipo_tercero: str, sufijo: str):

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    return TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": _documento(sufijo),
            "tipo_tercero": tipo_tercero,
            "razon_social": f"Exogena Demo {tipo_tercero} {sufijo}",
            "pais": "Colombia",
            "resp_r99_pn": True,
        },
    )


def _marcar_contabilizada_y_retener(
    modelo,
    factura_id: int,
    *,
    valor_retefuente: float = 0,
):

    from aplicacion.base_datos.conexion import SessionLocal

    db = SessionLocal()

    try:

        factura = (
            db.query(modelo)
            .filter(modelo.id == factura_id)
            .one()
        )

        factura.contabilizado = True
        factura.valor_retefuente = valor_retefuente

        db.commit()

    finally:

        db.close()


class TestServicioInformacionExogena:

    def test_pagos_y_retenciones_agrupa_por_proveedor(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.compras.facturas.modelos import (
            FacturaCompra,
        )
        from aplicacion.modulos.compras.facturas.servicios import (
            ServicioFacturaCompra,
        )
        from aplicacion.modulos.reportes.exogena.servicio import (
            ServicioInformacionExogena,
        )

        sufijo = _sufijo()

        proveedor = _crear_tercero(
            "Proveedor",
            sufijo,
        )

        factura = ServicioFacturaCompra.guardar_completa(
            {
                "proveedor_id": proveedor.id,
                "fecha": date.today(),
            },
            [
                {
                    "descripcion": "Servicio de prueba",
                    "cantidad": 1,
                    "precio_unitario": 500000,
                },
            ],
        )

        _marcar_contabilizada_y_retener(
            FacturaCompra,
            factura.id,
            valor_retefuente=17500,
        )

        filas = ServicioInformacionExogena.pagos_y_retenciones(
            date.today().year,
        )

        fila = next(
            f
            for f in filas
            if f["numero_documento"] == proveedor.numero_documento
        )

        assert fila["valor_base"] == 500000.0
        assert fila["valor_retefuente"] == 17500.0
        assert fila["nombre"] == proveedor.nombre_completo

    def test_ingresos_recibidos_agrupa_por_cliente(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.reportes.exogena.servicio import (
            ServicioInformacionExogena,
        )
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )
        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        sufijo = _sufijo()

        cliente = _crear_tercero(
            "Cliente",
            sufijo,
        )

        factura = ServicioFacturaVenta.guardar_completa(
            {
                "cliente_id": cliente.id,
                "fecha": date.today(),
            },
            [
                {
                    "descripcion": "Producto de prueba",
                    "cantidad": 2,
                    "precio_unitario": 100000,
                },
            ],
        )

        _marcar_contabilizada_y_retener(
            FacturaVenta,
            factura.id,
        )

        filas = ServicioInformacionExogena.ingresos_recibidos(
            date.today().year,
        )

        fila = next(
            f
            for f in filas
            if f["numero_documento"] == cliente.numero_documento
        )

        assert fila["valor_base"] == 200000.0

    def test_retenciones_que_le_practicaron_excluye_facturas_sin_retencion(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.reportes.exogena.servicio import (
            ServicioInformacionExogena,
        )
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )
        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        sufijo = _sufijo()

        cliente = _crear_tercero(
            "Cliente",
            sufijo,
        )

        factura = ServicioFacturaVenta.guardar_completa(
            {
                "cliente_id": cliente.id,
                "fecha": date.today(),
            },
            [
                {
                    "descripcion": "Producto de prueba",
                    "cantidad": 1,
                    "precio_unitario": 300000,
                },
            ],
        )

        _marcar_contabilizada_y_retener(
            FacturaVenta,
            factura.id,
            valor_retefuente=0,
        )

        filas = ServicioInformacionExogena.retenciones_que_le_practicaron(
            date.today().year,
        )

        assert not any(
            f["numero_documento"] == cliente.numero_documento
            for f in filas
        )

        _marcar_contabilizada_y_retener(
            FacturaVenta,
            factura.id,
            valor_retefuente=10500,
        )

        filas = ServicioInformacionExogena.retenciones_que_le_practicaron(
            date.today().year,
        )

        fila = next(
            f
            for f in filas
            if f["numero_documento"] == cliente.numero_documento
        )

        assert fila["valor_retefuente"] == 10500.0

    def test_pagos_y_retenciones_usa_datos_del_documento_sin_proveedor_id(
        self,
        requiere_postgresql,
    ):

        from aplicacion.base_datos.conexion import SessionLocal
        from aplicacion.modulos.compras.facturas.modelos import (
            FacturaCompra,
        )
        from aplicacion.modulos.compras.facturas.servicios import (
            ServicioFacturaCompra,
        )
        from aplicacion.modulos.reportes.exogena.servicio import (
            ServicioInformacionExogena,
        )

        sufijo = _sufijo()

        proveedor = _crear_tercero(
            "Proveedor",
            sufijo,
        )

        factura = ServicioFacturaCompra.guardar_completa(
            {
                "proveedor_id": proveedor.id,
                "fecha": date.today(),
            },
            [
                {
                    "descripcion": "Servicio importado",
                    "cantidad": 1,
                    "precio_unitario": 250000,
                },
            ],
        )

        db = SessionLocal()

        try:

            registro = (
                db.query(FacturaCompra)
                .filter(FacturaCompra.id == factura.id)
                .one()
            )

            registro.contabilizado = True
            registro.proveedor_id = None
            registro.nit_proveedor = _documento(sufijo)
            registro.razon_social_proveedor = (
                f"Proveedor XML {sufijo}"
            )

            db.commit()

        finally:

            db.close()

        filas = ServicioInformacionExogena.pagos_y_retenciones(
            date.today().year,
        )

        fila = next(
            f
            for f in filas
            if f["numero_documento"] == _documento(sufijo)
        )

        assert fila["nombre"] == f"Proveedor XML {sufijo}"
        assert fila["valor_base"] == 250000.0
