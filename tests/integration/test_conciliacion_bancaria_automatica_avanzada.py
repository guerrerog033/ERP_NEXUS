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


def _crear_tercero(
    sufijo: str,
    *,
    tipo_tercero: str = "Cliente",
):

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    return TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": _documento(sufijo),
            "tipo_tercero": tipo_tercero,
            "razon_social": f"Conciliación Avanzada Demo {sufijo}",
            "pais": "Colombia",
            "resp_r99_pn": True,
        },
    )


def _crear_extracto(
    *,
    valor: float,
    tipo: str,
    descripcion: str = "",
    referencia: str = "",
):

    from aplicacion.base_datos.conexion import SessionLocal
    from aplicacion.modulos.tesoreria.conciliacion.modelos import (
        ExtractoBancario,
    )

    db = SessionLocal()

    try:

        registro = ExtractoBancario(
            banco="Banco Demo",
            cuenta="123456",
            fecha=date.today(),
            descripcion=descripcion,
            referencia=referencia,
            valor=valor,
            tipo=tipo,
            origen="manual",
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        return registro.id

    finally:

        db.close()


def _crear_factura_venta(
    cliente_id: int,
    sufijo: str,
    *,
    total: float,
):

    from aplicacion.base_datos.conexion import SessionLocal
    from aplicacion.modulos.ventas.facturas.modelos import (
        FacturaVenta,
    )

    db = SessionLocal()

    try:

        registro = FacturaVenta(
            numero=f"FV-{sufijo}",
            fecha=date.today(),
            cliente_id=cliente_id,
            subtotal=total,
            total=total,
            saldo_pendiente=total,
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        return registro

    finally:

        db.close()


def _crear_factura_compra(
    proveedor_id: int,
    sufijo: str,
    *,
    total: float,
):

    from aplicacion.base_datos.conexion import SessionLocal
    from aplicacion.modulos.compras.facturas.modelos import (
        FacturaCompra,
    )

    db = SessionLocal()

    try:

        registro = FacturaCompra(
            numero=f"FC-{sufijo}",
            fecha=date.today(),
            proveedor_id=proveedor_id,
            subtotal=total,
            total=total,
            saldo_pendiente=total,
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        return registro

    finally:

        db.close()


class TestCombinacionFacturas:

    def test_un_pago_que_cubre_dos_facturas_las_concilia_ambas(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        factura_a = _crear_factura_venta(
            cliente.id,
            sufijo + "a",
            total=100000,
        )
        factura_b = _crear_factura_venta(
            cliente.id,
            sufijo + "b",
            total=150000,
        )

        extracto_id = _crear_extracto(
            valor=250000,
            tipo="credito",
        )

        resultado = ServicioConciliacionBancaria.conciliar_automatico()

        assert resultado["conciliados"] >= 1

        conciliaciones = [
            c
            for c in ServicioConciliacionBancaria.listar_conciliadas()
            if c.extracto_id == extracto_id
        ]

        ids_documento = {c.documento_id for c in conciliaciones}

        assert ids_documento == {factura_a.id, factura_b.id}
        assert all(c.estado == "combinado" for c in conciliaciones)

        pendientes = ServicioConciliacionBancaria.listar_pendientes()
        assert all(e.id != extracto_id for e in pendientes)

    def test_sin_combinacion_que_cuadre_queda_pendiente(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        _crear_factura_venta(
            cliente.id,
            sufijo + "a",
            total=70000,
        )
        _crear_factura_venta(
            cliente.id,
            sufijo + "b",
            total=90000,
        )

        extracto_id = _crear_extracto(
            valor=500000,
            tipo="credito",
        )

        ServicioConciliacionBancaria.conciliar_automatico()

        pendientes = {
            e.id for e in ServicioConciliacionBancaria.listar_pendientes()
        }

        assert extracto_id in pendientes

    def test_combinacion_tambien_aplica_a_facturas_de_compra(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        proveedor = _crear_tercero(
            sufijo,
            tipo_tercero="Proveedor",
        )

        factura_a = _crear_factura_compra(
            proveedor.id,
            sufijo + "a",
            total=40000,
        )
        factura_b = _crear_factura_compra(
            proveedor.id,
            sufijo + "b",
            total=60000,
        )

        extracto_id = _crear_extracto(
            valor=100000,
            tipo="debito",
        )

        ServicioConciliacionBancaria.conciliar_automatico()

        conciliaciones = [
            c
            for c in ServicioConciliacionBancaria.listar_conciliadas()
            if c.extracto_id == extracto_id
        ]

        ids_documento = {c.documento_id for c in conciliaciones}

        assert ids_documento == {factura_a.id, factura_b.id}


class TestPagoParcial:

    def test_pago_parcial_con_numero_en_referencia_concilia(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        factura = _crear_factura_venta(
            cliente.id,
            sufijo,
            total=500000,
        )

        extracto_id = _crear_extracto(
            valor=200000,
            tipo="credito",
            referencia=factura.numero,
        )

        ServicioConciliacionBancaria.conciliar_automatico()

        conciliaciones = [
            c
            for c in ServicioConciliacionBancaria.listar_conciliadas()
            if c.extracto_id == extracto_id
        ]

        assert len(conciliaciones) == 1
        assert conciliaciones[0].documento_id == factura.id
        assert conciliaciones[0].estado == "parcial"
        assert float(conciliaciones[0].valor) == 200000.0

    def test_pago_parcial_sin_numero_en_texto_no_concilia(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        _crear_factura_venta(
            cliente.id,
            sufijo,
            total=500000,
        )

        extracto_id = _crear_extracto(
            valor=200000,
            tipo="credito",
            referencia="transferencia sin referencia",
        )

        ServicioConciliacionBancaria.conciliar_automatico()

        pendientes = {
            e.id for e in ServicioConciliacionBancaria.listar_pendientes()
        }

        assert extracto_id in pendientes

    def test_match_exacto_tiene_prioridad_sobre_parcial(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        factura = _crear_factura_venta(
            cliente.id,
            sufijo,
            total=300000,
        )

        extracto_id = _crear_extracto(
            valor=300000,
            tipo="credito",
            referencia=factura.numero,
        )

        ServicioConciliacionBancaria.conciliar_automatico()

        conciliaciones = [
            c
            for c in ServicioConciliacionBancaria.listar_conciliadas()
            if c.extracto_id == extracto_id
        ]

        assert len(conciliaciones) == 1
        assert conciliaciones[0].estado == "conciliado"
